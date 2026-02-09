# journal/cron.py
from .news_fetcher import fetch_news
from .ai import run_automation

def auto_run_news():
    """Cette fonction sera appelée par le CRON automatiquement"""
    news = fetch_news()
    if news:
        run_automation(news)
