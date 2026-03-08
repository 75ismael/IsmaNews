from .news_fetcher import fetch_news  # Ton fichier ketch_news renommé ou importé
from .ai import write, detect_category, generate_news_image, send_report_email
from .models import Article, Category, AuthorProfile
from django.contrib.auth.models import User
from django.utils.text import slugify

def run():
    print("🚀 Démarrage de l'automatisation IsmaNews...")

    # 1. Récupération des news brutes
    news_list = fetch_news()
    articles_crees = []

    # 2. Récupération de l'auteur IA (ton profil)
    try:
        user_admin = User.objects.get(username="ismaelahamada")
        author_ia, _ = AuthorProfile.objects.get_or_create(user=user_admin)
    except User.DoesNotExist:
        print("❌ Erreur : L'utilisateur 'ismaelahamada' n'existe pas.")
        return

    # 3. Traitement de chaque news
    for n in news_list:
        try:
            # Éviter les doublons (basé sur l'URL source)
            if Article.objects.filter(source_url=n["url"]).exists():
                continue

            # IA : Rédaction du contenu détaillé
            full_text = write(n)

            # IA : Détection de la catégorie (France, Iran, etc.)
            cat_name = detect_category(full_text)
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': slugify(cat_name)}
            )

            # Création de l'article en base de données
            nouveau_art = Article.objects.create(
                title=n["title"],
                summary=full_text[:300] + "...",
                content=full_text,
                source=n["source"]["name"],
                source_url=n["url"],
                image_url=n.get("urlToImage"),
                category=cat,
                author=author_ia,
                status="draft" # On garde en brouillon pour validation
            )

            # 4. Génération de l'image de partage (avec Logo et Bandeau)
            if nouveau_art.image_url:
                # Cette fonction crée le visuel sur ton MacBook Air
                visuel_path = generate_news_image(nouveau_art.image_url, nouveau_art.title)
                print(f"📸 Visuel généré : {visuel_path}")

            articles_crees.append(nouveau_art)
            print(f"✅ Article ajouté : {nouveau_art.title[:50]}...")

        except Exception as e:
            print(f"⚠️ Erreur sur l'article {n.get('title')}: {e}")

    # 5. Envoi du rapport final par Email
    if articles_crees:
        send_report_email(articles_crees, len(articles_crees))
        print(f"📧 Rapport envoyé pour {len(articles_crees)} articles.")
    else:
        print("Empty-handed : Aucune nouvelle news à traiter.")

    print("🏁 Fin du cycle.")