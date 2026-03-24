import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from journal.models import Subscriber, Article

logger = logging.getLogger(__name__)

class NewsletterService:
    @staticmethod
    def sync_to_brevo(subscriber):
        """
        Placeholder for syncing to Brevo API.
        En vraie production, on utiliserait le SDK sib-api-v3-sdk ici.
        """
        logger.info(f"SIMULATION API BREVO: Synchronisation de {subscriber.email} réussie.")

    @staticmethod
    def send_daily_newsletter():
        """
        Génère et envoie la newsletter aux abonnés vérifiés.
        """
        subscribers = Subscriber.objects.filter(is_verified=True, wants_daily=True)
        if not subscribers.exists():
            print("Aucun abonné vérifié pour la newsletter.")
            return

        # On prend les 3 derniers articles générés par l'IA ou à la une
        top_articles = Article.objects.filter(status="published").order_by('-published_at')[:3]

        if not top_articles:
            print("Aucun article à envoyer.")
            return

        subject = "Votre Matinale IsmaNews - L'essentiel de l'actu"
        
        for sub in subscribers:
            context = {
                'articles': top_articles,
                'email': sub.email,
                'unsubscribe_url': f"http://127.0.0.1:8000/unsubscribe/{sub.email}/{sub.unsubscribe_token}/"
            }
            
            html_message = render_to_string('journal/newsletter_email.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    "Équipe IsmaNews <noreply@ismanews.com>",
                    [sub.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                print(f"Envoyé avec succès à : {sub.email}")
            except Exception as e:
                print(f"Erreur d'envoi à {sub.email} : {e}")
