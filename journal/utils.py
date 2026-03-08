from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives # Ajoute ça
from django.utils.html import strip_tags           # Ajoute ça
import requests
def send_validation_email(article_id, title):
    link = f"http://127.0.0.1:8000/approve/{article_id}/"
    send_mail(
        subject=f"Nouvel article à valider : {title}",
        message=f"Cliquez ici pour valider l'article : {link}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],  # ton mail
        fail_silently=False
    )

def post_to_facebook(image_path, message):
    """Publie une image et un message sur la page Facebook d'Alkamaria"""
    access_token = "EAAVMwt9pzZCMBQ340D0uSAynkoWZC8IRN0HnxZAyPiZBYN4VULB9XwL9BO1YCA8gykA91Xym8TJizisXH4ZBOECsBIytoHPwx22vFefs2UWmAsxu7FQdPy117uN1cJ85cZC87U91uuS4LZCF5R7LE16n85hHuhWiFDcRZBvarLP7UZCbWYaG6BtWqQAGNN1Ow0q7NbeZBBELdcO29wcI3ijZCAZALp5387CrIrHP".strip()
    page_id = "100133363118227"
    url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

    try:
        with open(image_path, 'rb') as img_file:
            files = {'source': img_file}
            data = {'message': message, 'access_token': access_token}
            response = requests.post(url, files=files, data=data)

            res_json = response.json()
            # On affiche TOUJOURS la réponse pour comprendre si ça rate
            print(f"📡 DEBUG FB RESPONSE: {res_json}")

            return res_json
    except Exception as e:
        print(f"❌ Erreur de connexion Facebook : {e}")
        return None


def send_report_email(articles, count):
    subject = f"📰 IsmaNews : {count} nouveaux articles"
    to = [settings.EMAIL_HOST_USER]
    items_html = "".join([f'<li><b>{a.category.name}</b>: {a.title}</li>' for a in articles])
    html_content = f"<html><body><h1>Rapport Alkamaria</h1><ul>{items_html}</ul></body></html>"
    msg = EmailMultiAlternatives(subject, strip_tags(html_content), settings.EMAIL_HOST_USER, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()




