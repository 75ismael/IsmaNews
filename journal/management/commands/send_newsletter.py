from django.core.management.base import BaseCommand
from journal.services.newsletter_service import NewsletterService

class Command(BaseCommand):
    help = 'Génère et envoie la newsletter quotidienne aux abonnés vérifiés.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Génération de la newsletter en cours...")
        NewsletterService.send_daily_newsletter()
        self.stdout.write(self.style.SUCCESS("Opération Newsletter terminée !"))
