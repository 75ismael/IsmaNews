from .news_fetcher import fetch_news
from .ai import write
from .models import Article

def run():
    news=fetch_news()
    for n in news:
        text=write(n)
        Article.objects.create(
            title=n["title"],
            summary=text[:300],
            content=text,
            source=n["source"]["name"],
            source_url=n["url"],
            published_at=n["publishedAt"]
        )

