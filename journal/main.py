import os
import sys
import logging
import django
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IsmaNews")

def setup_django():
    """Configures the Python path and Django environment."""
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(base_dir)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ismanews.settings')
    load_dotenv(os.path.join(base_dir, '.env'))
    try:
        django.setup()
        logger.info("Django initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Django: {e}")
        sys.exit(1)

def main():
    """Main execution flow."""
    setup_django()

    try:
        from news_fetcher import fetch_news
        from ai import process_news_cycle
    except ImportError as e:
        logger.error(f"Failed to import core modules: {e}")
        return

    logger.info("--- STARTING ISMANEWS CYCLE ---")

    # Fetch fresh news
    news_found = fetch_news()

    if news_found:
        process_news_cycle(news_found)
    else:
        logger.info("No new articles found this cycle.")

    logger.info("--- CYCLE COMPLETED ---")

if __name__ == "__main__":
    main()
# ... le reste de ton code ...