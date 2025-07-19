# Fichier réécrit à 100%
"""Tests unitaires pour le module utils.

Ce fichier vérifie la correction du nouveau modèle "Spline Unifiée".
"""

import numpy as np
import pytest

from utils import (
    MAX_LEVEL,
    XP_CUM_TABLE,
    calculer_bonus_de_palier,
    make_progress_bar,
    total_xp_to_level,
)


def test_xp_cum_table_generation():
    """Vérifie les propriétés fondamentales de la table d'XP générée."""
    assert len(XP_CUM_TABLE) == MAX_LEVEL + 1
    assert XP_CUM_TABLE[0] == 0
    assert np.all(np.diff(XP_CUM_TABLE) > 0)


def test_total_xp_to_level_conversion():
    """Vérifie que la conversion XP -> Niveau est correcte avec la nouvelle table."""
    assert total_xp_to_level(int(XP_CUM_TABLE[1]) - 1) == 0
    assert total_xp_to_level(int(XP_CUM_TABLE[1])) == 1
    assert total_xp_to_level(int(XP_CUM_TABLE[1]) + 1) == 1

    level_50_threshold = int(XP_CUM_TABLE[50])
    assert total_xp_to_level(level_50_threshold - 1) == 49
    assert total_xp_to_level(level_50_threshold) == 50
    assert total_xp_to_level(level_50_threshold + 1) == 50

    level_100_threshold = int(XP_CUM_TABLE[100])
    assert total_xp_to_level(level_100_threshold) == 100
    # Ligne reformatée pour respecter la limite de 88 caractères
    xp_over_max = level_100_threshold + 100000
    assert total_xp_to_level(xp_over_max) == 100


def test_calculer_bonus_de_palier():
    """Vérifie la logique des bonus de paliers (test de non-régression)."""
    assert calculer_bonus_de_palier(4) == 0
    assert calculer_bonus_de_palier(5) == 250
    assert calculer_bonus_de_palier(19) == 0
    assert calculer_bonus_de_palier(20) == 750
    assert calculer_bonus_de_palier(59) == 750
    assert calculer_bonus_de_palier(60) == 2500
    assert calculer_bonus_de_palier(99) == 2500
    assert calculer_bonus_de_palier(100) == 10000


def test_make_progress_bar():
    """Vérifie que la barre de progression est générée correctement."""
    # Lignes reformatées pour respecter la limite de 88 caractères
    expected_empty = "[░░░░░░░░░░░░]"
    assert make_progress_bar(0, 100, length=12) == expected_empty

    expected_half = "[██████░░░░░░]"
    assert make_progress_bar(50, 100, length=12) == expected_half

    expected_full = "[████████████]"
    assert make_progress_bar(100, 100, length=12) == expected_full

    # Test des cas limites
    assert make_progress_bar(150, 100, length=12) == expected_full
    assert make_progress_bar(10, 0, length=12) == expected_full
