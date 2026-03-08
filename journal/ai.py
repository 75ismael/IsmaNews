from PIL import ImageFilter, Image, ImageDraw, ImageFont, ImageEnhance
import textwrap
import os
import time
import requests
from io import BytesIO
from groq import Groq
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from journal.models import Category, Article, AuthorProfile
from journal.utils import post_to_facebook,send_report_email

# --- CONFIGURATION ---
client = Groq(api_key="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")
def write(article_data):
    """Génère un article de presse complet, humain et sans gras Markdown"""
    source_content = article_data.get('content') or article_data.get('description') or "Pas de contenu disponible."

    prompt = f"""
    Tu es le rédacteur en chef d'Alkamaria Global News. 
    Rédige un article captivant en français sur ce sujet : {source_content}

    CONSIGNES DE STYLE (ANTI-ROBOT) :
    - INTERDIT : Ne mets JAMAIS de texte en gras (pas de **).
    - INTERDIT : Bannis les mots d'IA : 'crucial', 'essentiel', 'complexe', 'au cœur de', 'foudroyant', 'pléthore'.
    - TON : Journalistique, direct. Évite les phrases bateaux comme "Les fans attendaient avec impatience".
    
    STRUCTURE :
    1. UNE ACCROCHE : Entre immédiatement dans le fait principal.
    2. DÉVELOPPEMENT : Explique les faits (pourquoi, comment, qui) avec des chiffres si possible.
    3. ENJEUX : Explique l'impact concret. Ne dis pas "Pourquoi c'est important", montre-le.
    4. CONCLUSION : Une phrase d'ouverture pour l'audience.

    IMPORTANT : N'écris PAS les noms des sections (ex: n'écris pas 'DÉVELOPPEMENT :'). Fais des paragraphes fluides.
    """

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7 # Ajoute un peu de naturel
    )

    content = completion.choices[0].message.content

    # --- SÉCURITÉ : NETTOYAGE DES ÉTIQUETTES ---
    # Si l'IA écrit quand même les titres de section, on les efface ici
    labels_to_remove = [
        "ACCROCHE :", "DÉVELOPPEMENT :", "ENJEUX :", "CONCLUSION :",
        "UNE ACCROCHE :", "🔍 CONCLUSION :", "🌍 ENJEUX :", "📝 DÉVELOPPEMENT :", "📰 UNE ACCROCHE :"
    ]

    for label in labels_to_remove:
        content = content.replace(label, "")

    # Nettoyage final du gras et des espaces inutiles
    content = content.replace("**", "").strip()

    return content
def detect_category(text):
    prompt = f"Donne uniquement un mot de catégorie (France, Iran, USA, Afrique, International) pour ce texte : {text[:200]}"
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return completion.choices[0].message.content.strip().replace(".", "")

def generate_news_image(base_image_url, title):
    try:
        response = requests.get(base_image_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGB")

        # 1. FORMAT PORTRAIT (1080x1350)
        target_width, target_height = 1080, 1350
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            new_width = int(target_height * img_ratio)
            img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
            left = (new_width - target_width) / 2
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            new_height = int(target_width / img_ratio)
            img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
            top = (new_height - target_height) / 2
            img = img.crop((0, top, target_width, top + target_height))

        # 2. EFFETS PRO
        img = ImageEnhance.Contrast(img).enhance(1.1)
        overlay = Image.new('RGBA', (1080, 1350), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for i in range(500):
            alpha = int((i / 500) * 230)
            draw.line([(0, 1350-i), (1080, 1350-i)], fill=(0, 0, 0, alpha))

        draw.rectangle([50, 1050, 58, 1280], fill=(26, 115, 232, 255))

        try:
            font = ImageFont.truetype("/Library/Fonts/Arial Bold.ttf", 55)
        except:
            font = ImageFont.load_default()

        lines = textwrap.wrap(title, width=32)
        y_text = 1060
        for line in lines[:4]:
            draw.text((82, y_text+2), line, font=font, fill=(0,0,0,120))
            draw.text((80, y_text), line, font=font, fill="white")
            y_text += 70

        img = Image.alpha_composite(img.convert("RGBA"), overlay)

        logo_path = os.path.join(settings.BASE_DIR, 'journal', 'static', 'journal', 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((200, 200))
            img.paste(logo, (830, 40), logo)

        file_name = f"share_{slugify(title[:20])}.jpg"
        save_path = os.path.join(settings.BASE_DIR, 'journal', 'news_shares', file_name)
        img.convert("RGB").save(save_path, "JPEG", quality=95)
        return save_path

    except Exception as e:
        print(f"❌ Erreur Image : {e}")
        return None

# --- AUTOMATION ---
def run_automation(news_list):
    print(f"🚀 Lancement de l'automatisation ({len(news_list)} articles potentiels)...")
    compteur = 0
    articles_crees = []

    try:
        user_admin = User.objects.get(username="ismaelahamada")
        author_ia, _ = AuthorProfile.objects.get_or_create(user=user_admin)
    except User.DoesNotExist:
        print("❌ Erreur : L'utilisateur 'ismaelahamada' n'existe pas.")
        return

    for item in news_list:
        try:
            if Article.objects.filter(source_url=item.get('url')).exists():
                continue

            content = write(item)
            cat_name = detect_category(content)
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})

            nouveau_art = Article.objects.create(
                title=item.get('title', 'Sans titre'),
                summary=content[:300] + "...",
                content=content,
                image_url=item.get('urlToImage'),
                source=item.get('source', {}).get('name', 'Inconnue'),
                source_url=item.get('url', ''),
                category=cat,
                author=author_ia,
                status="published",
                published_at=timezone.now()
            )

            if nouveau_art.image_url:
                visuel_local = generate_news_image(nouveau_art.image_url, nouveau_art.title)
                if visuel_local:
                    # CHANGEMENT ICI : On publie le contenu complet (content)
                    msg_fb = f"{nouveau_art.content}\n\n # Alkamaria Global News\n#News #{cat_name}"
                    fb_res = post_to_facebook(visuel_local, msg_fb)
                    if fb_res and 'id' in fb_res:
                        print(f"✅ Publié sur Facebook (ID: {fb_res['id']})")

            compteur += 1
            articles_crees.append(nouveau_art)
            print(f"🌟 Article '{nouveau_art.title[:40]}' terminé. ⏳ Pause 15s...")
            time.sleep(15)
        except Exception as e:
            print(f"❌ Erreur article : {e}")
            time.sleep(5)

    if compteur > 0: send_report_email(articles_crees, compteur)



