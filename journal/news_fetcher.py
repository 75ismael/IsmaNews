import requests

def fetch_news():
    api_key = "13c60d5d863e47e8bb3bf23a106f94ab"
    
    queries = ['France', 'Iran', 'USA', 'Comores', 'Afrique']
    all_articles = []
    
    # On cherche "Comores OR Afrique" pour avoir des sujets locaux
    # On trie par 'publishedAt' pour avoir les news les plus récentes
    for query in queries:
        print(f"📡 Recherche de news pour : {query}...")
        url = f'https://newsapi.org/v2/everything?q={query}&language=fr&sortBy=publishedAt&apiKey={api_key}'
        
        try:
            response = requests.get(url)
            data = response.json()
            if data.get('articles'):
                # On prend les 3 premiers de chaque recherche
                all_articles.extend(data['articles'][:3])
        except Exception as e:
            print(f"❌ Erreur NewsAPI pour {query}: {e}")
    return all_articles
