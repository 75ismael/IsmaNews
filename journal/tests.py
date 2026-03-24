from django.test import TestCase, Client
from django.core import mail
from django.urls import reverse
from journal.models import Subscriber

class NewsletterTestCase(TestCase):
    def setUp(self):
        # Initialisation du client de test (simulateur de navigateur)
        self.client = Client()
        self.test_email = "lecteur@ismanews.com"

    def test_subscriber_creation_tokens(self):
        """1. Vérifie que la création d'un Subscriber génère bien deux jetons uniques et sécurisés."""
        sub = Subscriber.objects.create(email=self.test_email)
        self.assertFalse(sub.is_verified)
        self.assertEqual(len(sub.verification_token), 64)
        self.assertEqual(len(sub.unsubscribe_token), 64)

    def test_subscribe_view_sends_email(self):
        """2. Vérifie l'envoi de l'email de confirmation (Double Opt-In)."""
        response = self.client.post(reverse('subscribe_newsletter'), {'email': self.test_email})
        self.assertEqual(response.status_code, 302)  # Redirection vers l'accueil après succès
        self.assertEqual(Subscriber.objects.count(), 1)
        
        # Vérifier que le mail est bien virtuellement parti
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Confirmez votre inscription", mail.outbox[0].subject)

    def test_verify_newsletter_token(self):
        """3. Vérifie que le clic sur le lien secret valide bien le compte (passe à is_verified=True)."""
        sub = Subscriber.objects.create(email=self.test_email)
        self.assertFalse(sub.is_verified)
        
        # Simuler le clic du lecteur sur le lien de son mail
        response = self.client.get(reverse('verify_newsletter', args=[sub.verification_token]))
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le statut en BDD a bien changé
        sub.refresh_from_db()
        self.assertTrue(sub.is_verified)

    def test_unsubscribe_deletes_user_data(self):
        """4. Vérifie l'effacement total et immédiat des données (Conformité RGPD)."""
        sub = Subscriber.objects.create(email=self.test_email, is_verified=True)
        self.assertEqual(Subscriber.objects.count(), 1)
        
        # Simuler le clic sur le lien "Se désabonner"
        url = reverse('unsubscribe_newsletter', kwargs={'email': sub.email, 'token': sub.unsubscribe_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # Action critique : L'utilisateur n'existe plus en BDD
        self.assertEqual(Subscriber.objects.count(), 0)
