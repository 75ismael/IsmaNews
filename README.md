# Alkamaria Global News 📰

**Alkamaria Global News** est un portail multimédia d'actualités multi-régional, intelligent et automatisé. Inspiré par les designs premium de **BBC News**, il propose une expérience d'information dense, dynamique et personnalisée selon la région du lecteur.

Ce projet démontre la puissance de l'intégration entre un framework web robuste (**Django**) et des modèles de langage avancés (**Llama 3 via Groq**) pour créer un média autonome et scalable.

---

## 🚀 Fonctionnalités Clés (Version "Complet")

- **Dashbord BBC-Style** : Une architecture de grille à 4 colonnes optimisée pour la densité d'information (Hero, Highlights, Live Flow, Popular).
- **Navigation Multi-Régionale** : Un menu latéral (**Side-Drawer**) dynamique permettant de basculer instantanément entre les éditions (France, Afrique, International, etc.).
- **Moteur Audio & Podcast** : Système de recommandation audio intelligent qui propose des podcasts adaptés à la région du lecteur avec un lecteur multimédia intégré.
- **Rédaction par IA Autonome** : Utilisation de **Groq / Llama 3** pour transformer des dépêches brutes en articles journalistiques structurés avec analyse et catégorisation.
- **CRM & Newsletter** : Système d'abonnement *Double Opt-In* (RGPD compliant) avec envoi automatisé de "La Matinale" en HTML riche.
- **Publication Sociale** : Auto-postage sur les réseaux sociaux (Facebook Graph API) pour maximiser la portée.

---

## 🛠️ Architecture Technique

Le projet repose sur une orchestration de services spécialisés :

1.  **Backend** : Django 6.0 (Stabilité et sécurité).
2.  **Intelligence Artificielle** : Groq API (Inférence ultra-rapide) pour la génération de contenu.
3.  **Frontend** : Vanilla CSS & JS (Sans frameworks lourds pour une performance maximale et un contrôle total du design).
4.  **Automatisation** : Cron Jobs pour les cycles de news et l'envoi des newsletters.

---

## 📂 Documentation de Référence

Pour une compréhension approfondie du projet (idéal pour un jury), consultez le dossier `docs/` :

- [🚀 Guide de Présentation (Anti-sèche)](docs/JURY_PRESENTATION_GUIDE.md) : Scénario de démo et questions techniques.
- [💎 Concept du Routage Dynamique](docs/CONCEPT_CLE_ROUTAGE_DYNAMIQUE.md) : Comment le site gère plusieurs pays avec un seul code.
- [🏗️ Architecture Globale](docs/ARCHITECTURE.md) : Anatomie complète des services.
- [⚙️ Aide-Mémoire des Commandes](docs/COMMANDS.md) : Toutes les commandes vitales (migrations, crontab, run_cycle).

---

## ⚙️ Installation Rapide

1.  **Cloner et Installer** :
    ```bash
    git clone https://github.com/75ismael/IsmaNews.git
    cd IsmaNews
    pip install -r requirements.txt
    ```
2.  **Configuration** :
    Créez un fichier `.env` basé sur `.env.example` avec vos API Keys (Groq, NewsAPI, Facebook).
3.  **Lancer le Moteur** :
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## 📄 Licence
Ce projet est sous licence MIT. Développé avec passion pour l'excellence journalistique numérique.
