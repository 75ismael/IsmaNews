import os
import logging
import requests
from typing import List, Dict
from dotenv import load_dotenv

# Initialize environment variables and logger
load_dotenv()
logger = logging.getLogger(__name__)

def fetch_news() -> List[Dict]:
    """
    Fetches news from NewsAPI based on predefined queries.
    Uses environment variables for security and logging for traceability.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        logger.error("NEWS_API_KEY not found in environment variables.")
        return []

    # Define queries
    me_query = "(Iran OR Teheran OR Moyen-Orient OR Liban OR Gaza)"
    sport_query = '(Football OR "Ligue 1" OR "Real Madrid" OR "Equipe de France" OR Basketball)'
    queries = [me_query, sport_query, 'France', 'USA', 'Comores', 'Afrique']
    
    all_articles = []

    for query in queries:
        display_name = "Iran/Moyen-Orient" if query == me_query else query
        logger.info(f"Searching news for: {display_name}...")

        # Remove language filter for Middle East to get global coverage
        lang = "" if query == me_query else "&language=fr"
        url = f'https://newsapi.org/v2/everything?q={query}{lang}&sortBy=publishedAt&apiKey={api_key}'

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'error':
                logger.warning(f"NewsAPI error for {display_name}: {data.get('message')}")
                continue

            articles = data.get('articles', [])
            if articles:
                limit = 4 if query == me_query else 2
                selection = articles[:limit]
                all_articles.extend(selection)
                logger.info(f"Found {len(selection)} articles for {display_name}")
            else:
                logger.info(f"No recent articles found for {display_name}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {display_name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching news for {display_name}: {e}")

    return all_articles