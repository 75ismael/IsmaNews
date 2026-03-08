# journal/context_processors.py
from .models import Category, Article, Newspaper

def global_journal_data(request):
    return {
        'categories': Category.objects.all(),
        'newspapers': Newspaper.objects.all(),
        'breaking': Article.objects.filter(status="published", is_breaking_news=True)[:5],
        # Ajoute ici popular et other_editions pour le footer
    }