import os
import time
import logging
import requests
import textwrap
from io import BytesIO
from typing import List, Dict, Optional
from PIL import ImageFilter, Image, ImageDraw, ImageFont, ImageEnhance
from groq import Groq
from django.utils import timezone
from django.utils.text import slugify
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
load_dotenv()
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
PROVIDER_API_KEY = os.getenv("GROQ_API_KEY")
if not PROVIDER_API_KEY:
    logger.error("API Key not found in environment variables.")
    client = None
else:
    client = Groq(api_key=PROVIDER_API_KEY)

def generate_article_content(article_data: Dict) -> str:
    """Generates a complete press article based on source data."""
    if not client:
        return "Content generation service not configured."

    source_content = article_data.get('content') or article_data.get('description') or "Pas de contenu disponible."

    prompt = f"""
    Rédige un article captivant en français sur ce sujet : {source_content}

    STYLE :
    - Ton : Journalistique, direct.
    
    STRUCTURE :
    - Une accroche directe.
    - Développement des faits.
    - Impact concret/enjeux.
    - Conclusion ouverte.

    IMPORTANT : Pas de titres de section. Fais des paragraphes fluides.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = completion.choices[0].message.content
        
        # Cleanup labels if AI ignored instructions
        labels_to_remove = [
            "ACCROCHE :", "DÉVELOPPEMENT :", "ENJEUX :", "CONCLUSION :",
            "UNE ACCROCHE :", "🔍 CONCLUSION :", " ENJEUX :", " DÉVELOPPEMENT :", " UNE ACCROCHE :"
        ]
        for label in labels_to_remove:
            content = content.replace(label, "")

        return content.replace("**", "").strip()
    except Exception as e:
        logger.error(f"Error during article generation: {e}")
        return "Erreur lors de la génération de l'article."

def detect_category(text: str) -> str:
    """Classifies an article into a category."""
    if not client:
        return "International"

    prompt = f"Donne uniquement un mot de catégorie (France, Iran, USA, Afrique, International) pour ce texte : {text[:200]}"
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return completion.choices[0].message.content.strip().replace(".", "")
    except Exception as e:
        logger.error(f"Error detecting category: {e}")
        return "International"

def generate_news_image(base_image_url: str, title: str) -> Optional[str]:
    """Generates a professional news visual with overlay."""
    try:
        response = requests.get(base_image_url, timeout=10)
        response.raise_for_status()
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

        # 2. PRO EFFECTS & OVERLAY
        img = ImageEnhance.Contrast(img).enhance(1.1)
        overlay = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Gradient bottom
        for i in range(500):
            alpha = int((i / 500) * 230)
            draw.line([(0, target_height-i), (target_width, target_height-i)], fill=(0, 0, 0, alpha))

        # Blue accent bar
        draw.rectangle([50, 1050, 58, 1280], fill=(26, 115, 232, 255))

        # Font handling
        try:
            # Common paths on macOS/Linux
            font_paths = ["/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
            font = None
            for path in font_paths:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, 55)
                    break
            if not font:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        lines = textwrap.wrap(title, width=32)
        y_text = 1060
        for line in lines[:4]:
            draw.text((82, y_text+2), line, font=font, fill=(0,0,0,120))
            draw.text((80, y_text), line, font=font, fill="white")
            y_text += 70

        img = Image.alpha_composite(img.convert("RGBA"), overlay)

        # Paste Logo
        logo_path = os.path.join(settings.BASE_DIR, 'journal', 'static', 'journal', 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((200, 200))
            img.paste(logo, (830, 40), logo)

        # Save
        file_name = f"share_{slugify(title[:20])}.jpg"
        save_dir = os.path.join(settings.BASE_DIR, 'journal', 'news_shares')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, file_name)
        img.convert("RGB").save(save_path, "JPEG", quality=95)
        return save_path

    except Exception as e:
        logger.error(f"Error generating visual for '{title}': {e}")
        return None

def process_news_cycle(news_list: List[Dict]):
    """Orchestrates the full news production workflow."""
    logger.info(f"Processing cycle for {len(news_list)} potential articles...")
    count = 0
    articles_created = []

    if not client:
        logger.error("Content service not available. Aborting.")
        return

    try:
        user_admin = User.objects.filter(is_superuser=True).first()
        if not user_admin:
            logger.error("No editor found to attribute articles.")
            return
        
        editor_profile, _ = AuthorProfile.objects.get_or_create(user=user_admin)
    except Exception as e:
        logger.error(f"Error setting up editor profile: {e}")
        return

    for item in news_list:
        try:
            source_url = item.get('url', '')
            if Article.objects.filter(source_url=source_url).exists():
                logger.info(f"Article already exists: {item.get('title')[:30]}...")
                continue

            content = generate_article_content(item)
            cat_name = detect_category(content)
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})

            article = Article.objects.create(
                title=item.get('title', 'Sans titre'),
                summary=content[:300] + "...",
                content=content,
                image_url=item.get('urlToImage'),
                source=item.get('source', {}).get('name', 'Inconnue'),
                source_url=source_url,
                category=cat,
                author=editor_profile,
                status="published",
                published_at=timezone.now()
            )

            # Optional Social Media Posting
            if article.image_url:
                visual_path = generate_news_image(article.image_url, article.title)
                if visual_path:
                    msg_fb = f"{article.content}\n\n # Alkamaria Global News\n#News #{cat_name}"
                    fb_res = post_to_facebook(visual_path, msg_fb)
                    if fb_res and 'id' in fb_res:
                        logger.info(f"Published on Facebook: {article.title[:40]}")

            count += 1
            articles_created.append(article)
            logger.info(f"Successfully processed article: '{article.title[:40]}'")
            time.sleep(15) # Rate limiting respect
            
        except Exception as e:
            logger.error(f"Error processing item: {e}")
            time.sleep(5)

    if count > 0:
        try:
            send_report_email(articles_created, count)
            logger.info(f"Report email sent for {count} articles.")
        except Exception as e:
            logger.error(f"Failed to send report email: {e}")



