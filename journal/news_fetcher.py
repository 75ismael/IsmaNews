import requests

def fetch_news():
    api_key = "13c60d5d863e47e8bb3bf23a106f94ab"

    # Requête simplifiée sans les apostrophes qui bloquent l'URL
    me_query = "(Iran OR Teheran OR Moyen-Orient OR Liban OR Gaza)"
    #sport_query = "(Football OR 'Ligue 1' OR Real Madrid OR 'Equipe de France' OR Basketball)"
    sport_query = '(Football OR "Ligue 1" OR "Real Madrid" OR "Equipe de France" OR Basketball)'

    queries = [me_query,sport_query, 'France', 'USA', 'Comores', 'Afrique']
    all_articles = []

    for query in queries:
        display_name = "Iran/Moyen-Orient" if query == me_query else query
        print(f" 🔍 Recherche de news pour : {display_name}...")

        # ASTUCE : On retire "&language=fr" pour le Moyen-Orient pour capter l'info mondiale
        # Ton IA Groq se chargera de traduire en français si l'article est en anglais !
        lang = "" if query == me_query else "&language=fr"

        url = f'https://newsapi.org/v2/everything?q={query}{lang}&sortBy=publishedAt&apiKey={api_key}'

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            # Debug : voir si l'API répond une erreur
            if data.get('status') == 'error':
                print(f" ⚠️ NewsAPI dit : {data.get('message')}")

            if data.get('articles'):
                limit = 4 if query == me_query else 2
                all_articles.extend(data['articles'][:limit])
                print(f" ✅ {len(data['articles'][:limit])} articles trouvés pour {display_name}")
            else:
                print(f" ℹ️ Aucun article récent trouvé pour {display_name}")

        except Exception as e:
            print(f" ❌ Erreur NewsAPI pour {display_name}: {e}")

    return all_articles