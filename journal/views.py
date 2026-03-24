from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import Article, Category, Newspaper, Comment

# --- ACCUEIL ---
def home(request, slug=None):
    all_newspapers = Newspaper.objects.all()

    # 1. Détection de la zone (URL propre)
    if slug:
        local_edition = get_object_or_404(Newspaper, slug=slug)
    else:
        # Édition par défaut sur la racine (International)
        local_edition = all_newspapers.filter(target_country='INT').first()
        if not local_edition:  # Sécurité
            local_edition = all_newspapers.first()

    # 2. Préparation du menu secondaire
    other_editions = all_newspapers.exclude(id=local_edition.id if local_edition else None)

    # 3. Filtrage des actualités par rapport à l'édition demandée
    breaking = Article.objects.filter(status="published", is_breaking_news=True)[:10] # On prend jusqu'à 10 breaking news
    
    headline = Article.objects.filter(status="published", is_headline=True, newspaper=local_edition).first()
    if not headline:
        headline = Article.objects.filter(status="published", is_headline=True).first()

    # Colonnes pour remplir l'espace (Saturer l'affichage)
    top_secondary = Article.objects.filter(status="published", newspaper=local_edition).exclude(id=headline.id if headline else None).order_by("-published_at")[:6]

    # 4. Sélection IA Granulaire (Rubrique + Catégorie)
    ai_picks = Article.objects.filter(status="published", is_ai_selection=True, newspaper=local_edition)
    
    featured_category = None
    if ai_picks.exists():
        featured_category = ai_picks.first().category
        ai_picks = ai_picks.filter(category=featured_category)[:3]
    else:
        ai_picks = Article.objects.filter(status="published", is_ai_selection=True)[:3]
        if ai_picks.exists():
            featured_category = ai_picks.first().category

    popular = Article.objects.filter(status="published").order_by("-views")[:5]
    
    # On s'assure que 'breaking' a assez d'articles pour remplir la colonne de droite (8 min)
    if breaking.count() < 8:
         extra = Article.objects.filter(status="published").exclude(Q(id__in=[b.id for b in breaking]) | Q(id=headline.id if headline else None))[:8-breaking.count()]
         breaking = list(breaking) + list(extra)
    else:
         breaking = breaking[:8]

    latest = Article.objects.filter(newspaper=local_edition, status="published").exclude(Q(id=headline.id if headline else None) | Q(id__in=[a.id for a in top_secondary])).order_by("-published_at")[:10]
    
    # --- AUDIO RECOMMANDÉ (Local vs International) ---
    recommended_audios = Article.objects.filter(status="published", is_audio_news=True, newspaper=local_edition)[:8]
    if not recommended_audios.exists():
        # Fallback sur l'international ou global
        recommended_audios = Article.objects.filter(status="published", is_audio_news=True)[:8]

    all_categories = Category.objects.all()

    return render(request, "journal/home.html", {
        "breaking": breaking,
        "headline": headline,
        "top_secondary": top_secondary,
        "ai_picks": ai_picks,
        "featured_category": featured_category,
        "newspapers": all_newspapers,
        "local_edition": local_edition,
        "other_editions": other_editions,
        "popular": popular,
        "latest": latest,
        "recommended_audios": recommended_audios,
        "all_categories": all_categories,
    })


def article_detail(request, pk):
    # Récupère l'article ou renvoie une erreur 404 s'il n'existe pas
    article = get_object_or_404(Article, pk=pk)
    
    # Calcul du temps de lecture : environ 200 mots par minute
    word_count = len(article.content.split())
    reading_time = max(1, word_count // 200) # Minimum 1 minute
    
    context = {
        'article': article,
        'reading_time': reading_time,
    }
    return render(request, 'journal/article.html', context)

def article(request, id):
    art = get_object_or_404(Article, id=id, status="published")
    
    # Traitement du nouveau commentaire s'il y en a un
    if request.method == "POST" and request.user.is_authenticated:
        text = request.POST.get('text')
        if text:
            Comment.objects.create(article=art, user=request.user, text=text)
            return redirect('article', id=id)

    # On augmente le compteur de vues uniquement pour les requêtes normales (GET)
    if request.method == "GET":
        art.views += 1
        art.save(update_fields=['views'])
    
    # Récupération des commentaires liés à l'article
    comments = Comment.objects.filter(article=art).order_by('-date')
    
    # Récupération d'articles similaires (Même catégorie)
    related_articles = Article.objects.filter(category=art.category, status="published").exclude(id=art.id).order_by('-published_at')[:3]
    if not related_articles: # Si peu d'articles dans la catégorie, on prend les derniers globaux
        related_articles = Article.objects.filter(status="published").exclude(id=art.id).order_by('-published_at')[:3]
    
    return render(request, "journal/article.html", {
        "article": art, 
        "comments": comments,
        "related_articles": related_articles
    })


# 3. Moteur de Recherche performant
def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        ).distinct()
    
    return render(request, 'journal/search_results.html', {
        'results': results,
        'query': query,
    })
# 4. Page par catégorie 
def category(request, category_slug, edition_slug=None):
    # 1. On récupère la catégorie
    cat = get_object_or_404(Category, slug=category_slug)

    # 2. On récupère les articles
    articles_list = Article.objects.filter(category=cat, status="published").order_by("-published_at")

    local_edition = None
    if edition_slug:
        local_edition = get_object_or_404(Newspaper, slug=edition_slug)
        articles_list = articles_list.filter(newspaper=local_edition)
    else:
        local_edition = Newspaper.objects.filter(target_country='INT').first()

    # 3. PAGINATION : 13 articles
    paginator = Paginator(articles_list, 13)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "journal/category.html", {
        "category": cat,
        "articles": page_obj,
        "local_edition": local_edition,
    })

# 5. Validation rapide (via email ou lien direct)
def approve(request, id):
    art = get_object_or_404(Article, id=id)
    art.status = "published"
    art.save()
    return redirect("/")

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

from django.contrib import messages
from .models import Subscriber

from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            sub = Subscriber.objects.filter(email=email).first()
            if sub and sub.is_verified:
                messages.warning(request, "Vous êtes déjà inscrit et vérifié !")
            else:
                if not sub:
                    sub = Subscriber.objects.create(email=email)
                elif not sub.verification_token:
                    sub.save()
                
                # Envoi de l'email de Double Opt-In
                verify_url = request.build_absolute_uri(reverse('verify_newsletter', args=[sub.verification_token]))
                subject = "Confirmez votre inscription à la newsletter IsmaNews"
                html_message = f'''
                <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                    <h2 style="color: #bc0000; text-align: center;">Bienvenue sur IsmaNews !</h2>
                    <p>Merci de vous être inscrit à notre newsletter d'alertes actualités.</p>
                    <p>Conformément au RGPD, veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous :</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verify_url}" style="background-color: #bc0000; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">Je confirme mon inscription</a>
                    </div>
                    <p style="font-size: 0.8rem; color: #888; text-align: center;">Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.</p>
                </div>
                '''
                try:
                    send_mail(
                        subject,
                        strip_tags(html_message),
                        "IsmaNews (Ne pas répondre) <noreply@ismanews.com>",
                        [email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    messages.success(request, "Dernière étape ! Un email de confirmation vous a été envoyé. Veuillez cliquer sur le lien pour valider votre inscription (vérifiez vos spams).")
                except Exception as e:
                    print(f"\n[!!! ERREUR D'ENVOI D'EMAIL !!!]")
                    print(f"Votre mot de passe d'application Gmail semble révoqué ou expiré : {e}")
                    print(f"Pour valider cet abonné manuellement, copiez/collez ce lien :")
                    print(verify_url)
                    print("---------------------------------\n")
                    messages.warning(request, "Erreur serveur : L'email de vérification n'a pas pu être envoyé à cause d'un blocage de Gmail (Identifiants invalides). Regardez votre console pour valider manuellement.")
    return redirect('/')

def verify_newsletter(request, token):
    sub = Subscriber.objects.filter(verification_token=token).first()
    if sub:
        if sub.is_verified:
            messages.warning(request, "Votre compte était déjà vérifié !")
        else:
            sub.is_verified = True
            sub.save()
            messages.success(request, "Félicitations ! Votre inscription est confirmée. Vous recevrez nos prochaines newsletters.")
    else:
        messages.error(request, "Lien de vérification invalide ou expiré.")
    return redirect('/')

def unsubscribe_newsletter(request, email, token):
    # Requette dans la base pour chrcher le mail avec token correspondant
    sub = Subscriber.objects.filter(email=email, unsubscribe_token=token).first()
    if sub:
        sub.delete()
        messages.success(request, "Désabonnement réussi. Vos données ont été effacées et vous ne recevrez plus nos alertes.")
    else:
        messages.error(request, "Lien de désabonnement invalide ou compte déjà supprimé.")
    return redirect('/')
