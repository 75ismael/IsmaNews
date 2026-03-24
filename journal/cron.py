# journal/cron.py
from journal.services.news_fetcher import fetch_news
from journal.services.ai_generator import process_news_cycle

def auto_run_news():
    """Cette fonction sera appelée par le CRON automatiquement"""
    news = fetch_news()
    if news:
        process_news_cycle(news)
