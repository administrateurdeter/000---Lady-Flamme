"""Tests unitaires pour le module utils.

Ce fichier vérifie la correction du nouveau modèle "Spline Unifiée".
"""

import numpy as np
import pytest

# On importe les fonctions et la table pré-calculée depuis le module à tester
from utils import (
    MAX_LEVEL,
    XP_CUM_TABLE,
    calculer_bonus_de_palier,
    make_progress_bar,
    total_xp_to_level,
)


def test_xp_cum_table_generation():
    """Vérifie les propriétés fondamentales de la table d'XP générée."""
    # La table doit avoir MAX_LEVEL + 1 entrées (de 0 à 100)
    assert len(XP_CUM_TABLE) == MAX_LEVEL + 1
    # Le niveau 0 doit coûter 0 XP
    assert XP_CUM_TABLE[0] == 0
    # La table doit être strictement croissante
    assert np.all(np.diff(XP_CUM_TABLE) > 0)


def test_total_xp_to_level_conversion():
    """Vérifie que la conversion XP -> Niveau est correcte avec la nouvelle table."""
    # Juste avant le seuil du niveau 1
    assert total_xp_to_level(int(XP_CUM_TABLE[1]) - 1) == 0
    # Exactement sur le seuil du niveau 1
    assert total_xp_to_level(int(XP_CUM_TABLE[1])) == 1
    # Juste après le seuil du niveau 1
    assert total_xp_to_level(int(XP_CUM_TABLE[1]) + 1) == 1

    # Test à un niveau plus élevé
    level_50_threshold = int(XP_CUM_TABLE[50])
    assert total_xp_to_level(level_50_threshold - 1) == 49
    assert total_xp_to_level(level_50_threshold) == 50

    # Test au niveau maximum
    level_100_threshold = int(XP_CUM_TABLE[100])
    assert total_xp_to_level(level_100_threshold) == 100
    assert total_xp_to_level(level_100_threshold + 100000) == 100


def test_calculer_bonus_de_palier():
    """Vérifie la logique des bonus de paliers."""
    assert calculer_bonus_de_palier(4) == 0
    assert calculer_bonus_de_palier(5) == 250
    assert calculer_bonus_de_palier(19) == 0
    assert calculer_bonus_de_palier(20) == 750
    assert calculer_bonus_de_palier(60) == 2500
    assert calculer_bonus_de_palier(100) == 10000


def test_make_progress_bar():
    """Vérifie que la barre de progression est générée correctement."""
    assert make_progress_bar(0, 100) == "[░░░░░░░░░░░░]"
    assert make_progress_bar(50, 100) == "[██████░░░░░░]"
    assert make_progress_bar(100, 100) == "[████████████]"
    assert make_progress_bar(150, 100) == "[████████████]"
    assert make_progress_bar(10, 0) == "[████████████]"
