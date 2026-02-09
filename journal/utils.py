from django.core.mail import send_mail
from django.conf import settings
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


def post_facebook(title, link, token):
    url = f"https://graph.facebook.com/v19.0/PAGE_ID/feed"
    payload = {"message": title + "\n" + link, "access_token": token}
    r = requests.post(url, data=payload)
    return r.json()

