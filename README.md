# Lady Flamme - Bot Discord de Progression et d'Économie

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python)
![discord.py](https://img.shields.io/badge/discord.py-2.5.1-5865F2?style=for-the-badge&logo=discord)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4-D71F00?style=for-the-badge&logo=sqlalchemy)

Un bot Discord sophistiqué conçu pour créer une expérience de communauté engageante grâce à un système de progression et d'économie sur-mesure. Le cœur du bot est le modèle "Spline Unifiée", une courbe de leveling conçue pour un équilibre parfait entre engagement à court terme et prestige à long terme.

---

## ✨ Philosophie du Projet

Ce bot n'est pas un simple compteur de messages. Il est le fruit d'une recherche approfondie en game design pour répondre à des objectifs stricts :

-   **Prestige à Long Terme :** Atteindre le niveau maximum est un véritable exploit, un voyage de plusieurs années.
-   **Équilibre Juste :** Le système est conçu pour récompenser la fidélité sans créer d'écarts insurmontables entre les membres très actifs et les membres occasionnels.
-   **Progression Organique :** La difficulté augmente de manière parfaitement lisse, sans "murs" frustrants, grâce à une modélisation mathématique par spline cubique.
-   **Économie Stable :** Un système économique à deux vitesses (salaire quotidien + primes de fidélité) assure que tous les membres peuvent participer tout en récompensant la persévérance.

---

## 🚀 Installation et Lancement

### Prérequis

-   Python 3.10 ou supérieur
-   Un serveur de base de données (PostgreSQL recommandé pour la production, SQLite pour le développement)

### Étapes d'installation

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/votre-nom/lady-flamme.git
    cd lady-flamme
    ```

2.  **Créer un environnement virtuel :**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurer les variables d'environnement :**
    Créez un fichier `.env` à la racine du projet en vous basant sur le modèle ci-dessous :
    ```env
    # .env

    # Token de votre bot Discord
    DISCORD_BOT_TOKEN="VOTRE_TOKEN_ICI"

    # ID du serveur (Guilde) où les slash commands seront synchronisées
    GUILD_ID="VOTRE_ID_DE_SERVEUR_ICI"

    # URL de connexion à votre base de données
    # Pour PostgreSQL (recommandé) :
    # DATABASE_URL="postgresql://user:password@host:port/database"
    # Pour SQLite (développement) :
    DATABASE_URL="sqlite:///dev_plok.db"
    ```

5.  **Lancer le bot :**
    Le `launcher.py` est le point d'entrée recommandé car il gère la relance automatique.
    ```bash
    python launcher.py
    ```

---

## 🛠️ Commandes Disponibles

### Commandes Utilisateur (Slash Commands)

-   `/rank [user]` : Affiche votre niveau, XP et progression (ou ceux d'un autre membre).
-   `/leaderboard` : Affiche le top 10 du serveur.
-   `/sac` : Affiche votre solde d'Ignis et votre inventaire.
-   `/shop` : Affiche les objets disponibles dans la boutique.
-   `/buy <item_id>` : Permet d'acheter un objet.

### Commandes Administrateur (Préfixe `!`)

-   `!reload_all` : Recharge tous les cogs sans redémarrer le bot.
-   `!recalculate_levels` : **[MAINTENANCE]** Recalcule le niveau de tous les utilisateurs. À n'utiliser qu'après une modification de la courbe d'XP.

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez consulter le fichier `CONTRIBUTING.md` pour connaître les normes de code et le flux de travail des Pull Requests.