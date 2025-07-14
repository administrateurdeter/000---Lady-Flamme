# tests/test_utils.py

import pytest
from utils import total_xp_to_level, make_progress_bar, xp_cum


def test_total_xp_to_level():
    """Vérifie que la conversion de l'XP en niveau est correcte."""
    # Le premier seuil pour le niveau 1 est xp_cum[0]
    level_1_threshold = xp_cum[0]  # Devrait être 583

    # Test au niveau 0
    assert total_xp_to_level(0) == 0
    assert total_xp_to_level(level_1_threshold - 1) == 0  # Juste avant le seuil

    # Test au niveau 1
    assert total_xp_to_level(level_1_threshold) == 1  # Exactement sur le seuil
    assert total_xp_to_level(level_1_threshold + 1) == 1  # Juste après le seuil

    # Test à un niveau plus élevé (le niveau 30 est atteint à 58379 XP)
    level_30_threshold = xp_cum[29]  # xp_cum est indexé de 0 à 99
    assert total_xp_to_level(level_30_threshold - 1) == 29
    assert total_xp_to_level(level_30_threshold) == 30


def test_make_progress_bar():
    """Vérifie que la barre de progression est générée correctement."""
    # Test barre vide
    assert make_progress_bar(0, 100) == "[░░░░░░░░░░░░]"

    # Test barre à moitié pleine
    assert make_progress_bar(50, 100) == "[██████░░░░░░]"

    # Test barre pleine
    assert make_progress_bar(100, 100) == "[████████████]"

    # Test de dépassement (doit être capé à 100%)
    assert make_progress_bar(150, 100) == "[████████████]"

    # Test de cas limite (division par zéro)
    assert make_progress_bar(10, 0) == "[████████████]"
