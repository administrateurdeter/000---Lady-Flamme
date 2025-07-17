"""Fonctions utilitaires et calculs mathématiques.

Ce module contient la logique de calcul de la courbe de progression "Spline Unifiée",
qui est le cœur du système de leveling. Il pré-calcule une table de recherche
pour des performances optimales.
"""

import logging
from typing import List

import numpy as np
from scipy.interpolate import CubicSpline

from config import XPConfig

logger = logging.getLogger(__name__)

# ==============================================================================
# MODÈLE DE PROGRESSION "SPLINE UNIFIÉE"
# ==============================================================================

# --- CONSTANTES FONDAMENTALES (importées depuis config.py) ---
PHI: float = XPConfig.PHI
CIBLE_MESSAGES_PER_DAY: int = XPConfig.CIBLE_MESSAGES_PER_DAY
MAX_LEVEL: int = XPConfig.MAX_LEVEL
KNOT_LEVELS: List[int] = XPConfig.KNOT_LEVELS
OPTIMAL_KNOT_VALUES: List[float] = XPConfig.OPTIMAL_KNOT_VALUES
LEVELS_NP: np.ndarray = np.arange(1, MAX_LEVEL + 1)


def get_unified_xp_table() -> np.ndarray:
    """Calcule et retourne la table d'XP cumulé pour les 100 niveaux.

    Cette fonction est le cœur du système "Spline Unifiée".
    Elle ne doit être exécutée qu'une seule fois au démarrage du bot.

    Returns:
        Un tableau NumPy où l'index `i` contient le seuil d'XP total
        nécessaire pour atteindre le niveau `i+1`. La table est de taille
        MAX_LEVEL+1, avec l'index 0 valant 0.
    """
    # --- Étape 1: Calcul du gain de référence de la Cible ---
    daily_xp_cible = sum(
        200 / (1 + PHI * n) for n in range(1, CIBLE_MESSAGES_PER_DAY + 1)
    )
    logger.info(
        f"[Spline] Gain journalier de référence (Cible) calculé: "
        f"{daily_xp_cible:.2f} XP/jour"
    )

    # --- Étape 2: Création de la fonction Spline qui modélise le temps ---
    spline_func = CubicSpline(KNOT_LEVELS, OPTIMAL_KNOT_VALUES, bc_type="natural")

    # --- Étape 3: Calcul du temps requis (en jours) pour chaque niveau ---
    days_per_level = spline_func(LEVELS_NP)

    # --- Étape 4: Conversion du temps en XP requis pour chaque niveau ---
    xp_req_per_level = days_per_level * daily_xp_cible

    # --- Étape 5: Calcul de l'XP cumulé nécessaire pour atteindre chaque niveau ---
    xp_cumulative_table = np.cumsum(xp_req_per_level)

    # --- Étape 6: Ajout d'un 0 au début pour que l'index corresponde au niveau ---
    # XP_CUM_TABLE[0] = 0 (pour le niveau 0)
    # XP_CUM_TABLE[1] = seuil pour atteindre le niveau 1.
    final_table = np.insert(xp_cumulative_table, 0, 0)
    logger.info(
        f"[Spline] Table d'XP Unifiée générée. "
        f"XP pour Lvl 100: {final_table[-1]:,.0f} XP"
    )
    return final_table


# --- EXÉCUTION DU PRÉ-CALCUL AU DÉMARRAGE ---
XP_CUM_TABLE: np.ndarray = get_unified_xp_table()


def total_xp_to_level(xp: int) -> int:
    """Calcule le niveau d'un utilisateur à partir de son XP total.

    Args:
        xp: Le montant total d'XP de l'utilisateur.

    Returns:
        Le niveau actuel de l'utilisateur.
    """
    # searchsorted est extrêmement rapide pour trouver l'index dans une table triée.
    # 'right' signifie que si xp == XP_CUM_TABLE[i], il retourne i.
    # On soustrait 1 pour obtenir le niveau actuel.
    # Ex: XP_CUM_TABLE = [0, 300, 900]. xp=299 -> searchsorted=1 -> level=0.
    # xp=300 -> searchsorted=2 -> level=1.
    level = np.searchsorted(XP_CUM_TABLE, xp, side="right") - 1
    return int(max(0, level))  # Assure de ne jamais retourner un niveau négatif


def calculer_bonus_de_palier(niveau_atteint: int) -> int:
    """Calcule le bonus d'or pour un palier de 5 niveaux.

    La logique économique est conservée pour récompenser la persévérance.

    Args:
        niveau_atteint: Le nouveau niveau que le joueur vient d'atteindre.

    Returns:
        Le montant du bonus en Ignis, ou 0 si aucun bonus n'est accordé.
    """
    if niveau_atteint == 0 or niveau_atteint % 5 != 0:
        return 0
    if niveau_atteint == 100:
        return 10000
    if 1 <= niveau_atteint <= 19:
        return 250
    elif 20 <= niveau_atteint <= 59:
        return 750
    elif 60 <= niveau_atteint <= 99:
        return 2500
    return 0


def make_progress_bar(current: int, needed: int, length: int = 12) -> str:
    """Génère une barre de progression textuelle simple et propre.

    Args:
        current: La progression actuelle (ex: XP depuis le dernier niveau).
        needed: La progression totale nécessaire pour le prochain palier.
        length: La longueur en caractères de la barre.

    Returns:
        Une chaîne de caractères représentant la barre de progression.
    """
    if needed <= 0:
        # Évite la division par zéro et affiche une barre pleine.
        current, needed = 1, 1
    percent: float = max(0.0, min(1.0, current / needed))
    filled_length: int = int(length * percent)
    bar: str = "█" * filled_length + "░" * (length - filled_length)
    return f"[{bar}]"