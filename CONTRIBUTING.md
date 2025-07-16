# Guide de Contribution au Projet Lady Flamme

Merci de votre intérêt pour ce projet ! Pour garantir la qualité et la cohérence du code, nous vous demandons de suivre ces quelques règles simples.

## 📝 Normes de Code

Le projet suit des normes de codage strictes pour assurer sa lisibilité et sa maintenabilité. Avant de soumettre votre code, veuillez vous assurer qu'il respecte les points suivants :

1.  **Formatage avec `black` :** Tout le code doit être formaté avec `black` en utilisant la configuration du projet (`line-length = 88`).
2.  **Linting avec `flake8` :** Le code ne doit générer aucune erreur `flake8`.
3.  **Typage Statique avec `mypy` :** Bien que non strict, nous encourageons l'ajout d'annotations de type partout où c'est possible.
4.  **Documentation :** Toute nouvelle fonction ou classe doit être documentée en suivant le format des docstrings Google (voir les fichiers existants pour des exemples).

Vous pouvez vérifier votre code localement en lançant :

    black .
    flake8 .
    mypy .

## Git Workflow : Comment Contribuer

Nous utilisons un flux de travail basé sur les **Pull Requests** pour intégrer les modifications. Ne pushez jamais directement sur la branche `main`.

### Étape 1 : Fork et Clonage

1.  **Forkez** le dépôt sur votre propre compte GitHub.
2.  **Clonez** votre fork sur votre machine locale.

### Étape 2 : Création d'une Branche

Créez une nouvelle branche pour chaque fonctionnalité ou correction de bug. Utilisez des noms de branche clairs et préfixés.

-   Pour une nouvelle fonctionnalité : `feat/nom-de-la-fonctionnalite` (ex: `feat/add-casino-game`)
-   Pour une correction de bug : `fix/description-du-bug` (ex: `fix/leaderboard-display-error`)
-   Pour une refactorisation : `refactor/portee-du-refactor` (ex: `refactor/database-caching`)

    git checkout -b feat/nom-de-la-fonctionnalite

### Étape 3 : Le Commit Parfait

Nous suivons la convention **Conventional Commits**. C'est une norme simple qui rend l'historique Git extrêmement lisible et permet de générer des changelogs automatiquement.

**Structure d'un message de commit :**

    <type>(<scope>): <sujet>

    [corps optionnel]

    [pied de page optionnel, ex: BREAKING CHANGE]

-   **`type` :** `feat` (nouvelle fonctionnalité), `fix` (correction de bug), `docs` (documentation), `style` (formatage), `refactor`, `test`, `chore` (maintenance).
-   **`scope` (optionnel) :** La partie du code affectée (ex: `xp`, `db`, `economy`).
-   **`sujet` :** Une description concise, à l'impératif, en minuscules.

**Exemple de bon commit :**

    feat(economy): add blackjack game to the casino

    Implements the full logic for a multiplayer blackjack game,
    including betting, hitting, and standing. A 5% house rake
    is applied to all winnings to serve as a money sink.

**Exemple de commit avec un Breaking Change :**

    refactor(xp): implement Spline Unifiée progression model

    Replaces the old XP curve with a new, more balanced model.

    BREAKING CHANGE: User levels must be recalculated post-deployment
    by running the `!recalculate_levels` command.

### Étape 4 : La Pull Request

Une fois votre travail terminé et commité, pushez votre branche sur votre fork et ouvrez une Pull Request vers la branche `main` du dépôt principal.

-   Donnez un titre clair à votre PR.
-   Dans la description, expliquez les changements que vous avez apportés et pourquoi.
-   Si votre PR résout une issue existante, mentionnez-la avec `Closes #123`.

Votre PR sera ensuite revue, et une fois approuvée, elle sera mergée. Merci pour votre contribution !