import os
import logging
import requests
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from dotenv import load_dotenv

# Initialize logger
logger = logging.getLogger(__name__)
load_dotenv()

def send_validation_email(article_id: int, title: str):
    """Sends an email for article validation."""
    base_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    link = f"{base_url}/approve/{article_id}/"
    try:
        send_mail(
            subject=f"Nouvel article à valider : {title}",
            message=f"Cliquez ici pour valider l'article : {link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False
        )
        logger.info(f"Validation email sent for article {article_id}")
    except Exception as e:
        logger.error(f"Failed to send validation email: {e}")

def post_to_facebook(image_path: str, message: str) -> dict:
    """Publishes an image and a message to the configured Facebook page."""
    access_token = os.getenv("FB_ACCESS_TOKEN")
    page_id = os.getenv("FB_PAGE_ID")
    
    if not access_token or not page_id:
        logger.error("Facebook credentials missing in environment variables.")
        return None

    url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

    try:
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            data = {'message': message, 'access_token': access_token}
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            
            res_json = response.json()
            logger.info(f"Successfully posted to Facebook. Response ID: {res_json.get('id')}")
            return res_json
    except requests.exceptions.RequestException as e:
        logger.error(f"Facebook Graph API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Facebook post: {e}")
        return None

def send_report_email(articles: list, count: int):
    """Sends a summary report of newly published articles."""
    subject = f" IsmaNews : {count} nouveaux articles"
    to = [settings.EMAIL_HOST_USER]
    
    items_html = "".join([f'<li><b>{a.category.name}</b>: {a.title}</li>' for a in articles])
    html_content = f"<html><body><h1>Rapport de Publication</h1><ul>{items_html}</ul></body></html>"
    
    try:
        msg = EmailMultiAlternatives(subject, strip_tags(html_content), settings.EMAIL_HOST_USER, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Report email sent for {count} articles.")
    except Exception as e:
        logger.error(f"Failed to send report email: {e}")




