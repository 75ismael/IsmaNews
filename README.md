# IsmaNews 📰

**IsmaNews** est un journal numérique innovant et entièrement automatisé. Propulsé par l'intelligence artificielle, il capture l'actualité mondiale en temps réel, rédige des articles complets et les publie de manière autonome.

Ce projet a été conçu pour démontrer l'intégration de flux de données externes avec des modèles de langage avancés (LLM) au sein d'une architecture de gestion de contenu robuste.

---

## 🚀 Fonctionnalités Clés

- **Extraction Intelligente** : Récupération automatisée des actualités via NewsAPI (ciblant la France, l'Iran, et d'autres régions stratégiques).
- **Rédaction par IA** : Utilisation de **Groq / Llama 3** pour transformer des dépêches brutes en articles structurés, engageants et optimisés pour la lecture.
- **Gestion de Contenu (CMS)** : Interface d'administration Django permettant la validation humaine (draft/publié), la gestion des catégories et des auteurs.
- **Automatisation Totale** : Système de tâches planifiées (Cron) déclenchant le cycle de production toutes les 4 heures.
- **SEO & Performance** : Slugs automatiques, architecture légère et interface réactive.

---

## 🛠️ Architecture Technique

Le projet repose sur un circuit fermé d'automatisation :

1.  **NewsAPI** : Source de données pour les actualités mondiales.
2.  **Groq (Llama 3)** : Moteur d'intelligence artificielle pour la rédaction et la catégorisation.
3.  **Django** : Framework web pour le stockage, l'administration et le rendu.
4.  **Django-Crontab** : Planificateur de tâches pour l'orchestration du backend.

---

## 📂 Structure du Projet

- `journal/` : Application principale contenant la logique métier.
    - `models.py` : Structure de la base de données (Articles, Catégories, etc.).
    - `news_fetcher.py` : Script de récupération des news.
    - `ai.py` : Intégration avec Groq/Llama 3.
    - `cron.py` : Orchestrateur des tâches automatiques.
- `ismanews/` : Configuration globale du projet Django.
- `static/` : Ressources statiques (images, CSS).
- `manage.py` : Point d'entrée pour les commandes de gestion Django.

---

## ⚙️ Installation et Configuration

### Prérequis
- Python 3.x
- Clé API NewsAPI
- Clé API Groq

### Installation
1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/votre-username/ismanews.git
    cd ismanews
    ```
2.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configurer les variables d'environnement** :
    Créez un fichier `.env` à la racine et ajoutez vos clés API.
4.  **Appliquer les migrations** :
    ```bash
    python manage.py migrate
    ```
5.  **Lancer le serveur** :
    ```bash
    python manage.py runserver
    ```

---

## 📈 Perspectives d'Évolution
- [ ] Refonte complète du design (UI/UX) pour une esthétique premium.
- [ ] Ajout d'une application mobile (React Native) via une API REST.
- [ ] Support multilingue pour les articles générés.

---

## 📄 Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
