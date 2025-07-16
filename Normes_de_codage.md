# Cahier des Charges des Normes de Codage - Projet "Lady Flamme"

---

## **1. Norme de Documentation (Docstrings & Commentaires)**

**L'objectif** est qu'un nouveau développeur puisse comprendre l'intention de n'importe quelle partie du code sans avoir à vous poser de questions.

- **Docstrings de Module (Haut de Fichier)** :  
  Chaque fichier .py commencera par un docstring `"""..."""` expliquant son rôle global dans l'application.

- **Docstrings de Classe** :  
  Chaque classe commencera par un docstring expliquant sa responsabilité.

- **Docstrings de Fonction/Méthode (Format Google)** :  
  Chaque fonction, méthode ou coroutine suivra un format strict :
  - Une ligne de résumé impérative ("Calcule...", "Gère...", "Récupère...").
  - Une description plus détaillée si nécessaire.
  - Une section **Args:** pour décrire chaque paramètre.
  - Une section **Returns:** pour décrire la valeur de retour.
  - Une section **Raises:** pour décrire les exceptions possibles.

- **Commentaires en ligne (#)** :  
  Les commentaires en ligne ne doivent **JAMAIS** expliquer ce que le code fait (le code doit être lisible), mais **POURQUOI** une décision a été prise. Ils clarifient l'intention.  
  Exemple : `# Verrouille la ligne pour éviter les race conditions lors d'un achat.`

- **Séparateurs Logiques** :  
  Les fonctions complexes seront structurées avec des commentaires de section  
  `# --- Étape 1: ... ---` pour guider la lecture.

---

## **2. Norme de Nommage (PEP 8 Strict)**

- **Variables & Fonctions** : `snake_case` (ex: `rebuild_cache`)
- **Classes** : `PascalCase` (ex: `CommandsCog`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `MAX_LEVEL`)
- **Membres "Internes"** : Un préfixe `_` sera utilisé pour les variables ou méthodes qui ne sont pas destinées à être utilisées à l'extérieur du module/classe (ex: `_flush_loop`).

---

## **3. Norme de Typage (PEP 484 Strict)**

- **Couverture Totale** : 100% des signatures de fonctions et de méthodes doivent avoir des annotations de type.
- **Précision** : Utilisation des types les plus précis possibles (`discord.Interaction` plutôt que `Any`, `np.ndarray` pour les tableaux NumPy).
- **Clarté** : Les imports du module typing (`List`, `Dict`, `Tuple`, `Optional`, etc.) seront utilisés systématiquement.

---

## **4. Norme de Structure et de Lisibilité**

- **Imports** :  
  Les imports seront groupés en trois blocs, séparés par une ligne vide, et alphabétiques à l'intérieur de chaque bloc :
  - Bibliothèque standard Python (`logging`, `os`, `math`)
  - Bibliothèques tierces (`discord`, `numpy`, `sqlalchemy`)
  - Modules de l'application locale (`config`, `db`, `utils`)

- **f-strings** :  
  L'utilisation des f-strings sera standardisée pour tout formatage de chaînes de caractères.

- **Formatage black** :  
  Le code sera formaté pour passer la vérification `black --check .