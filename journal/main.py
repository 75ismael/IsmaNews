import os
import sys
import django

# 1. On ajoute le dossier parent au chemin de recherche de Python
# Cela permet à Python de "voir" le dossier ismanews qui est au-dessus
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. On définit le module de réglages
# Ici, on utilise le nom du dossier qui contient ton settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ismanews.settings')

# 3. Initialisation de Django
try:
    django.setup()
    print("✅ Django est initialisé avec succès !")
except Exception as e:
    print(f"❌ Erreur d'initialisation : {e}")

# 4. Import des scripts (UNIQUEMENT après django.setup())
from news_fetcher import fetch_news
from ai import run_automation

if __name__ == "__main__":
    print("--- 🏁 DÉMARRAGE DU CYCLE ISMANEWS ---")

    # On va chercher les news
    news_fraiches = fetch_news()

    if news_fraiches:
        run_automation(news_fraiches)
    else:
        print("📭 Aucune nouvelle news trouvée.")

    print("--- ✅ CYCLE TERMINÉ ---")
# ... le reste de ton code ...