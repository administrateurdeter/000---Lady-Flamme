"""Service pour la logique métier de l'économie.

Ce module est indépendant de Discord. Il gère les opérations sur les
données des utilisateurs (solde, inventaire) et peut être réutilisé
ailleurs si nécessaire.
"""

from typing import Any, Dict

from db import atomic_purchase, fetch_user


class InsufficientFunds(Exception):
    """Exception levée quand un utilisateur n'a pas assez d'argent pour un achat."""

    pass


class EconomyService:
    """Contient la logique pour gérer le solde et les achats des utilisateurs."""

    def get_balance(self, user_id: int) -> int:
        """Récupère le solde d'un utilisateur.

        Args:
            user_id: L'ID Discord de l'utilisateur.

        Returns:
            Le solde en Ignis de l'utilisateur.
        """
        user: Dict[str, Any] = fetch_user(user_id)
        return user.get("coins", 0)

    def purchase(self, user_id: int, price: int, item_name: str) -> Dict[str, Any]:
        """Tente d'effectuer un achat pour un utilisateur de manière atomique.

        Args:
            user_id: L'ID de l'acheteur.
            price: Le prix de l'objet.
            item_name: Le nom de l'objet à ajouter à l'inventaire.

        Returns:
            Les données de l'utilisateur mises à jour après l'achat.

        Raises:
            InsufficientFunds: Si le solde de l'utilisateur est inférieur au prix.
        """
        success, message = atomic_purchase(
            user_id=user_id, item_name=item_name, price=price
        )

        if not success:
            raise InsufficientFunds(message)

        return fetch_user(user_id)
