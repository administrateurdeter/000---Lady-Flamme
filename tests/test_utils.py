"""Tests unitaires pour le module utils.

Ce fichier vérifie la correction du nouveau modèle "Spline Unifiée".
"""

import numpy as np
import pytest

# On importe les fonctions et la table pré-calculée depuis le module à tester
# Il est crucial d'importer depuis le module réel pour tester le résultat final
from utils import (
    MAX_LEVEL,
    XP_CUM_TABLE,
    calculer_bonus_de_palier,
    make_progress_bar,
    total_xp_to_level,
)


def test_xp_cum_table_generation():
    """Vérifie les propriétés fondamentales de la table d'XP générée."""
    # --- Vérification 1: La structure de la table ---
    # La table doit avoir MAX_LEVEL + 1 entrées (de 0 à 100)
    assert len(XP_CUM_TABLE) == MAX_LEVEL + 1

    # --- Vérification 2: Le point de départ ---
    # Le niveau 0 doit coûter 0 XP
    assert XP_CUM_TABLE[0] == 0

    # --- Vérification 3: La monotonie ---
    # La table doit être strictement croissante (chaque niveau coûte plus que le précédent)
    assert np.all(np.diff(XP_CUM_TABLE) > 0)


def test_total_xp_to_level_conversion():
    """Vérifie que la conversion XP -> Niveau est correcte avec la nouvelle table."""
    # --- Test 1: Cas de base (Niveau 0 et 1) ---
    # Juste avant le seuil du niveau 1
    assert total_xp_to_level(int(XP_CUM_TABLE[1]) - 1) == 0
    # Exactement sur le seuil du niveau 1 (on est toujours au niveau 0, on vient de le compléter)
    assert total_xp_to_level(int(XP_CUM_TABLE[1])) == 0
    # Juste après le seuil du niveau 1 (on est maintenant niveau 1)
    assert total_xp_to_level(int(XP_CUM_TABLE[1]) + 1) == 1

    # --- Test 2: Cas à un niveau intermédiaire (Niveau 50) ---
    level_50_threshold = int(XP_CUM_TABLE[50])
    assert total_xp_to_level(level_50_threshold - 1) == 49
    assert total_xp_to_level(level_50_threshold) == 49
    assert total_xp_to_level(level_50_threshold + 1) == 50

    # --- Test 3: Cas au niveau maximum ---
    level_100_threshold = int(XP_CUM_TABLE[100])
    assert total_xp_to_level(level_100_threshold) == 99
    # Toute XP supplémentaire ne doit pas changer le niveau au-delà de 100
    assert total_xp_to_level(level_100_threshold + 100000) == 100


def test_calculer_bonus_de_palier():
    """Vérifie la logique des bonus de paliers (test de non-régression)."""
    assert calculer_bonus_de_palier(4) == 0
    assert calculer_bonus_de_palier(5) == 250
    assert calculer_bonus_de_palier(19) == 0
    assert calculer_bonus_de_palier(20) == 750
    # CORRECTION : On teste un vrai multiple de 5 dans cette plage, comme 55.
    assert calculer_bonus_de_palier(55) == 750
    assert calculer_bonus_de_palier(60) == 2500
    assert calculer_bonus_de_palier(95) == 2500
    assert calculer_bonus_de_palier(100) == 10000


def test_make_progress_bar():
    """Vérifie que la barre de progression est générée correctement (test de non-régression)."""
    assert make_progress_bar(0, 100, length=12) == "[░░░░░░░░░░░░]"
    assert make_progress_bar(50, 100, length=12) == "[██████░░░░░░]"
    assert make_progress_bar(100, 100, length=12) == "[████████████]"
    # Test des cas limites
    assert (
        make_progress_bar(150, 100, length=12) == "[████████████]"
    )  # Doit être capé à 100%
    assert (
        make_progress_bar(10, 0, length=12) == "[████████████]"
    )  # Doit gérer la division par zéro
