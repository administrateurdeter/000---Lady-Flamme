"""
Fonctions utilitaires et calculs mathématiques.

Ce module contient la logique de calcul de la courbe d'XP et des bonus
de paliers, qui sont complexes et isolées ici pour plus de clarté.
"""

import math
from typing import List


def calculer_bonus_de_palier(niveau_atteint: int) -> int:
    """
    Calcule le bonus d'or pour un palier de 5 niveaux,
    en utilisant le modèle de scaling par paliers de difficulté.
    """
    # La fonction ne s'applique que si le niveau est un multiple de 5
    if niveau_atteint == 0 or niveau_atteint % 5 != 0:
        return 0

    if niveau_atteint == 100:
        return 10000  # Le jackpot final

    if 1 <= niveau_atteint <= 19:
        return 250
    elif 20 <= niveau_atteint <= 59:
        return 750
    elif 60 <= niveau_atteint <= 99:
        return 2500

    return 0


# --- Configuration de la courbe de leveling ---
MAX_LEVEL: int = 100

# Phase 1 (Niveaux 1-30)
_PHASE1_MAX_LVL: int = 30
_PHASE1_XP_AT_30: int = 58_379
_PHASE1_EXPONENT: float = 1.4

# Phase 2 (Niveaux 31-100)
_PHASE2_FINAL_XP: int = 1_902_556
_PHASE2_B: float = 0.0457423466

# --- Pré-calcul de la table d'XP cumulée ---
_exp30: float = math.exp(_PHASE2_B * _PHASE1_MAX_LVL)
_exp100: float = math.exp(_PHASE2_B * MAX_LEVEL)
_A: float = (_PHASE2_FINAL_XP - _PHASE1_XP_AT_30) / (_exp100 - _exp30)
_C: float = _PHASE1_XP_AT_30 - _A * _exp30

xp_cum: List[int] = []
for L in range(1, MAX_LEVEL + 1):
    xp_value: float
    if L <= _PHASE1_MAX_LVL:
        xp_value = _PHASE1_XP_AT_30 * (L / _PHASE1_MAX_LVL) ** _PHASE1_EXPONENT
    else:
        xp_value = _C + _A * math.exp(_PHASE2_B * L)
    xp_cum.append(int(round(xp_value)))


def total_xp_to_level(xp: int) -> int:
    """Calcule le niveau d'un utilisateur à partir de son XP total."""
    level: int = 0
    for threshold in xp_cum:
        if xp < threshold:
            break
        level += 1
    return level


def make_progress_bar(current: int, needed: int, length: int = 12) -> str:
    """Génère une barre de progression textuelle simple et propre."""
    if needed <= 0:
        current, needed = 1, 1  # Évite la division par zéro.
    percent: float = max(0.0, min(1.0, current / needed))
    filled_length: int = int(length * percent)
    bar: str = "█" * filled_length + "░" * (length - filled_length)
    return f"[{bar}]"