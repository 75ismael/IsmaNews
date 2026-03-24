import logging
from django.core.management.base import BaseCommand
from journal.services.news_fetcher import fetch_news
from journal.services.ai_generator import process_news_cycle

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetches new articles from NewsAPI and processes them via Groq AI.'

    def handle(self, *args, **options):
        logger.info("--- STARTING ISMANEWS CYCLE (Management Command) ---")
        self.stdout.write(self.style.SUCCESS("--- STARTING ISMANEWS CYCLE ---"))

        # Fetch fresh news
        self.stdout.write("Fetching fresh news...")
        news_found = fetch_news()

        if news_found:
            self.stdout.write(f"Found {len(news_found)} potential articles. Processing...")
            process_news_cycle(news_found)
            self.stdout.write(self.style.SUCCESS(f"Cycle completed. Processing finished."))
        else:
            logger.info("No new articles found this cycle.")
            self.stdout.write(self.style.WARNING("No new articles found this cycle."))

        logger.info("--- CYCLE COMPLETED ---")
