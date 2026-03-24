# journal/context_processors.py
from django.urls import resolve
from .models import Category, Article, Newspaper

def global_journal_data(request):
    current_edition = None
    try:
        match = resolve(request.path_info)
        if match.url_name == 'newspaper_detail' and 'slug' in match.kwargs:
            current_edition = Newspaper.objects.filter(slug=match.kwargs['slug']).first()
        elif match.url_name == 'category_in_edition' and 'edition_slug' in match.kwargs:
            current_edition = Newspaper.objects.filter(slug=match.kwargs['edition_slug']).first()
        elif match.url_name == 'home':
            current_edition = Newspaper.objects.filter(target_country='INT').first()
            if not current_edition:
                current_edition = Newspaper.objects.first()
    except Exception:
        pass

    # Dynamic thematic menu computation
    if current_edition:
        valid_cat_ids = Article.objects.filter(status="published", newspaper=current_edition).values_list('category', flat=True).distinct()
        cats = Category.objects.filter(id__in=valid_cat_ids)
    else:
        cats = Category.objects.all()

    return {
        'categories': cats,
        'newspapers': Newspaper.objects.all(),
        'breaking': Article.objects.filter(status="published", is_breaking_news=True)[:5],
        'active_edition': current_edition
    }