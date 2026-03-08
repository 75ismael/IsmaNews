from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Article, Category,Newspaper

def home(request):
    # 1. Détection de la zone (Simulation ou via GeoIP)
    # Dans la vraie vie, on utiliserait GeoIP2 ici.
    # Pour l'instant, on regarde si un pays est forcé dans l'URL, sinon on met 'INT'
    user_country_code = request.GET.get('country', 'INT')

    all_newspapers = Newspaper.objects.all()
   

    # 2. On sélectionne LE journal prioritaire pour l'utilisateur
    # On cherche celui qui match le pays, sinon on prend l'International
    local_edition = all_newspapers.filter(target_country=user_country_code).first()
    
    # Si aucun match (ex: utilisateur en Espagne), on prend l'édition par défaut
    if not local_edition:
        local_edition = all_newspapers.filter(target_country='INT').first()

    # 3. On prépare les autres éditions (pour le menu secondaire)
    other_editions = all_newspapers.exclude(id=local_edition.id if local_edition else None)

    # --- TES AUTRES FILTRES ---
    breaking = Article.objects.filter(status="published", is_breaking_news=True)[:5]
    headline = Article.objects.filter(status="published", is_headline=True).first()
    ai_picks = Article.objects.filter(status="published", is_ai_selection=True)[:3]
    popular = Article.objects.filter(status="published").order_by("-views")[:5]
    latest = Article.objects.filter(status="published").exclude(id=headline.id if headline else None)[:10]

    return render(request, "journal/home.html", {
        "breaking": breaking,
        "headline": headline,
        "ai_picks": ai_picks,
        "newspapers": all_newspapers,
        "local_edition": local_edition,  # On envoie l'édition "majeure"
        "other_editions": other_editions, # On envoie le reste "mineur"
        "popular": popular,
        "latest": latest,
    })
    
def newspaper_detail(request, slug):
    """Affiche uniquement les articles d'un journal (ex: IsmaNews Afrique)"""
    journal = get_object_or_404(Newspaper, slug=slug)
    articles = Article.objects.filter(newspaper=journal, status="published").order_by("-published_at")
    
    return render(request, "journal/newspaper_home.html", {
        "newspaper": journal,
        "articles": articles

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
    
    # On augmente le compteur de vues à chaque visite
    art.views += 1
    art.save()
    
    return render(request, "journal/article.html", {"article": art})


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
        'categories': Category.objects.all()
    })
# 4. Page par catégorie (Ex: France, USA, Iran)
def category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=cat, status="published").order_by("-published_at")
    return render(request, "journal/category.html", {
        "category": cat,
        "articles": articles
    })

# 5. Validation rapide (via email ou lien direct)
def approve(request, id):
    art = get_object_or_404(Article, id=id)
    art.status = "published"
    art.save()
    return redirect("/")
