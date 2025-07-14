"""
Service pour la logique métier de l'économie.

Ce module est indépendant de Discord. Il gère les opérations sur les
données des utilisateurs (solde, inventaire) et peut être réutilisé
ailleurs si nécessaire.
"""

from db import fetch_user, atomic_purchase
from typing import Any, Dict


class InsufficientFunds(Exception):
    """Exception levée quand un utilisateur n'a pas assez d'argent pour un achat."""

    pass


class EconomyService:
    """Contient la logique pour gérer le solde et les achats des utilisateurs."""

    def get_balance(self, user_id: int) -> int:
        """Récupère le solde d'un utilisateur."""
        user: Dict[str, Any] = fetch_user(user_id)
        return user.get("coins", 0)

    def purchase(self, user_id: int, price: int, item_name: str) -> Dict[str, Any]:
        """
        Tente d'effectuer un achat pour un utilisateur de manière atomique et sécurisée.
        
        Lève une exception InsufficientFunds si l'achat échoue.
        Retourne les données de l'utilisateur mises à jour en cas de succès.
        """

        success, message = atomic_purchase(
            user_id=user_id, item_name=item_name, price=price
        )

        if not success:
            raise InsufficientFunds(message)

        return fetch_user(user_id)