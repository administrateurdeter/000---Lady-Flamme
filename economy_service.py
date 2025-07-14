"""
Service pour la logique métier de l'économie.

Ce module est indépendant de Discord. Il gère les opérations sur les
données des utilisateurs (solde, inventaire) et peut être réutilisé
ailleurs si nécessaire.
"""

from db import fetch_user, save_user
from typing import Any, Dict, List


class InsufficientFunds(Exception):
    """Exception levée quand un utilisateur n'a pas assez d'argent pour un achat."""

    pass


class EconomyService:
    """Contient la logique pour gérer le solde et les achats des utilisateurs."""

    def get_balance(self, user_id: int) -> int:
        """Récupère le solde d'un utilisateur."""
        user: Dict[str, Any] = fetch_user(user_id)
        return user["money"]

    def purchase(self, user_id: int, price: int, item_name: str) -> Dict[str, Any]:
        """Tente d'effectuer un achat pour un utilisateur."""
        user: Dict[str, Any] = fetch_user(user_id)
        if user["money"] < price:
            raise InsufficientFunds(f"Solde insuffisant ({user['money']} < {price})")

        user["money"] -= price
        inv: Dict[str, Any] = user.get("inventory", {})
        items: List[str] = inv.get("items", [])
        items.append(item_name)
        inv["items"] = items
        user["inventory"] = inv

        save_user(user_id, user)
        return user
