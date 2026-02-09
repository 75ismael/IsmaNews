from groq import Groq
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Category, Article, AuthorProfile

client = Groq(api_key="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")

def write(article_data):
    source_content = article_data.get('content') or article_data.get('description') or "Pas de contenu."
    prompt = f"Rédige un article de presse professionnel et détaillé en français sur ce sujet : {source_content}"
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

def detect_category(text):
    prompt = f"Donne uniquement un mot de catégorie (France, Iran, USA, Afrique, International) pour ce texte : {text[:200]}"
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return completion.choices[0].message.content.strip().replace(".", "")
def run_automation(news_list):
    print(f"🚀 Traitement de {len(news_list)} actualités...")
    compteur = 0
    
    try:
        user_admin = User.objects.get(username="ismaelahamada")
        author_ia, _ = AuthorProfile.objects.get_or_create(user=user_admin)
    except User.DoesNotExist:
        print("❌ Erreur : L'utilisateur 'ismaelahamada' n'existe pas.")
        return

    for article in news_list:
        try:
            content = write(article)
            cat_name = detect_category(content)
            cat_slug = slugify(cat_name)
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': cat_slug}
            )

            Article.objects.create(
                title=article.get('title', 'Sans titre'),
                summary=content[:300] + "...",
                content=content,
                image_url=article.get('urlToImage'),
                source=article.get('source', {}).get('name', 'Inconnue'),
                source_url=article.get('url', ''),
                category=cat,
                author=author_ia,
                status="draft",
                published_at=timezone.now()
            )

            compteur += 1
            print(f"✅ Article ajouté : {article.get('title')[:30]}...")

        except Exception as e:
            print(f"❌ Erreur article : {e}")

    # 📩 Envoi du mail uniquement si au moins un article a été créé
    if compteur > 0:
        send_mail(
            "Alerte — Nouveaux articles générés par l’IA",
            f"""
            Bonjour Ismael,

            {compteur} nouveaux articles ont été générés automatiquement par le système IsmaNews et sont en attente de validation.

            Merci de vous connecter à votre espace d’administration pour les vérifier, les corriger et les publier.

            Cordialement,
            Le système IsmaNews
            """,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        print("📧 Email de notification envoyé.")
