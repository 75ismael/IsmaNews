import os
import requests
from io import BytesIO
from groq import Groq
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from .models import Category, Article, AuthorProfile

# --- CONFIGURATION ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "VOTRE_CLE_GROQ"))

# --- LOGIQUE IA (CONTENU) ---

def write(article_data):
    """Génère le corps de l'article via Llama 3.3"""
    source_content = article_data.get('content') or article_data.get('description') or "Pas de contenu."
    prompt = f"Rédige un article de presse professionnel et détaillé en français sur ce sujet : {source_content}"
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

def detect_category(text):
    """Détermine la catégorie la plus adaptée"""
    prompt = f"Donne uniquement un mot de catégorie (France, Iran, USA, Afrique, International) pour ce texte : {text[:200]}"
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return completion.choices[0].message.content.strip().replace(".", "")

# --- LOGIQUE IMAGE (VISUEL PRO) ---

def generate_news_image(base_image_url, title, logo_path="static/img/logo.png"):
    """Transforme l'image source en visuel style BFM/BBC avec logo et bandeau"""
    try:
        response = requests.get(base_image_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGB")

        # 1. Transformation artistique (Différenciation)
        width, height = img.size
        zoom = 0.10
        img = img.crop((width * zoom, height * zoom, width * (1 - zoom), height * (1 - zoom)))
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Color(img).enhance(1.2)

        # 2. Redimensionnement Facebook (1200x630)
        img = img.resize((1200, 630), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img, "RGBA")

        # 3. Bandeau News (Style Journal Télévisé)
        draw.rectangle([0, 460, 1200, 630], fill=(0, 0, 0, 170)) # Fond noir transparent
        draw.rectangle([0, 460, 20, 630], fill=(26, 115, 232, 255)) # Barre bleue

        # 4. Ajout du Texte
        try:
            font = ImageFont.truetype("arialbd.ttf", 42)
        except:
            font = ImageFont.load_default()

        draw.text((55, 490), title[:75] + ("..." if len(title) > 75 else ""), font=font, fill="white")

        # 5. Insertion du Logo
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((160, 160))
            img.paste(logo, (1010, 30), logo)

        # 6. Sauvegarde
        output_dir = os.path.join(settings.MEDIA_ROOT, "news_shares")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_name = f"share_{slugify(title[:30])}.jpg"
        save_path = os.path.join(output_dir, file_name)
        img.save(save_path, "JPEG", quality=90)
        return save_path
    except Exception as e:
        print(f"❌ Erreur Image : {e}")
        return None

# --- LOGIQUE RÉSEAUX SOCIAUX ---

def post_to_facebook(image_path, message):
    """Publie l'image générée sur la page Facebook"""
    fb_page_id = "VOTRE_PAGE_ID"
    access_token = "VOTRE_ACCESS_TOKEN"
    url = f"https://graph.facebook.com/{fb_page_id}/photos"

    try:
        with open(image_path, 'rb') as f:
            files = {'source': f}
            data = {'message': message, 'access_token': access_token}
            response = requests.post(url, files=files, data=data)
            return response.json()
    except Exception as e:
        print(f"❌ Erreur Facebook : {e}")
        return None

# --- FONCTION PRINCIPALE (AUTOMATION) ---

def run_automation(news_list):
    print(f"🚀 Lancement de l'automatisation ({len(news_list)} articles)...")
    compteur = 0
    articles_crees = []

    try:
        user_admin = User.objects.get(username="ismaelahamada")
        author_ia, _ = AuthorProfile.objects.get_or_create(user=user_admin)
    except User.DoesNotExist:
        print("❌ Erreur : Utilisateur 'ismaelahamada' introuvable.")
        return

    for item in news_list:
        try:
            # Doublons check
            if Article.objects.filter(source_url=item.get('url')).exists():
                continue

            # 1. Génération Contenu
            content = write(item)
            cat_name = detect_category(content)
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})

            # 2. Sauvegarde Django
            nouveau_art = Article.objects.create(
                title=item.get('title', 'Sans titre'),
                summary=content[:300] + "...",
                content=content,
                image_url=item.get('urlToImage'),
                source=item.get('source', {}).get('name', 'Inconnue'),
                source_url=item.get('url', ''),
                category=cat,
                author=author_ia,
                status="draft",
                published_at=timezone.now()
            )

            # 3. Génération Visuel Professionnel
            if nouveau_art.image_url:
                visuel_path = generate_news_image(nouveau_art.image_url, nouveau_art.title)

                if visuel_path:
                    print(f"📸 Visuel généré pour : {nouveau_art.title[:30]}")
                    # 4. Publication Facebook (Optionnel ici, ou après validation admin)
                    # msg = f"🔴 {nouveau_art.title}\n\nLire l'article : {settings.SITE_URL}/news/{nouveau_art.id}"
                    # post_to_facebook(visuel_path, msg)

            compteur += 1
            articles_crees.append(nouveau_art)

        except Exception as e:
            print(f"❌ Erreur article : {e}")

    # 5. Rapport Email
    if compteur > 0:
        send_report_email(articles_crees, compteur)

def send_report_email(articles, count):
    """Envoie le récapitulatif HTML des articles générés"""
    subject = f"📰 IsmaNews : {count} nouveaux articles à valider"
    from_email = f"IsmaNews System <{settings.EMAIL_HOST_USER}>"
    to = [settings.EMAIL_HOST_USER]

    items_html = "".join([f'<li style="margin-bottom:10px;"><b>{a.category.name}</b>: {a.title}</li>' for a in articles])

    html_content = f"""
    <html>
        <body style="font-family: Arial; line-height: 1.6;">
            <div style="background:#1a73e8; color:white; padding:20px; text-align:center;">
                <h1>IsmaNews AI Report</h1>
            </div>
            <div style="padding:20px;">
                <p>Bonjour Ismael, {count} articles ont été rédigés et mis en brouillon.</p>
                <ul>{items_html}</ul>
                <p>Transmission sécurisée via segments TCP/TLS.</p>
            </div>
        </body>
    </html>"""

    msg = EmailMultiAlternatives(subject, strip_tags(html_content), from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print(f"📧 Rapport mail envoyé.")