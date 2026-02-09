from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Article, Category

def home(request):
    articles = Article.objects.filter(status="published").order_by("-published_at")
    # On récupère les 5 articles les plus vus
    popular_articles = Article.objects.filter(status="published").order_by("-views")[:5]
    categories = Category.objects.all()
    
    return render(request, "journal/home.html", {
        "articles": articles,
        "popular_articles": popular_articles,
        "categories": categories
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
        # Recherche insensible à la casse dans le titre OU le contenu
        results = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        ).distinct()
    
    categories = Category.objects.all()
    return render(request, 'journal/search_results.html', {
        'results': results,
        'query': query,
        'categories': categories
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
