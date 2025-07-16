"""Tests unitaires pour le service de l'économie (EconomyService)."""

from typing import Any, Dict

import pytest
from pytest_mock import MockerFixture

from economy_service import EconomyService, InsufficientFunds


def test_purchase_successful(mocker: MockerFixture):
    """Vérifie qu'un achat réussi déduit le solde et ajoute l'objet.

    Args:
        mocker: Le plugin pytest-mock pour simuler des fonctions.
    """
    # --- 1. Préparation (Arrange) ---
    service = EconomyService()
    user_id = 123
    item_price = 100
    item_name = "test_item"

    # On simule les fonctions de la base de données pour isoler le service.
    mocker.patch(
        "economy_service.atomic_purchase", return_value=(True, "Achat réussi !")
    )
    fetch_mock = mocker.patch(
        "economy_service.fetch_user",
        return_value={"user_id": user_id, "coins": 400, "items": [item_name]},
    )

    # --- 2. Action (Act) ---
    updated_user = service.purchase(user_id, item_price, item_name)

    # --- 3. Vérification (Assert) ---
    assert updated_user["coins"] == 400
    assert item_name in updated_user["items"]
    fetch_mock.assert_called_once_with(user_id)


def test_purchase_insufficient_funds(mocker: MockerFixture):
    """Vérifie qu'une exception est levée si les fonds sont insuffisants.

    Args:
        mocker: Le plugin pytest-mock pour simuler des fonctions.
    """
    # --- 1. Préparation (Arrange) ---
    service = EconomyService()
    user_id = 456
    item_price = 1000
    error_message = "Solde insuffisant."

    # On simule un échec de la transaction atomique.
    mocker.patch("economy_service.atomic_purchase", return_value=(False, error_message))
    fetch_mock = mocker.patch("economy_service.fetch_user")

    # --- 2. Action & 3. Vérification (Act & Assert) ---
    # On vérifie que l'exception `InsufficientFunds` est bien levée.
    with pytest.raises(InsufficientFunds, match=error_message):
        service.purchase(user_id, item_price, "expensive_item")

    # On vérifie que fetch_user n'a jamais été appelé après l'échec.
    fetch_mock.assert_not_called()
