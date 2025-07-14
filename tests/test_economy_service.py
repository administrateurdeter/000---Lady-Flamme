# tests/test_economy_service.py

import pytest
from economy_service import EconomyService, InsufficientFunds


# Le 'mocker' est un outil fourni par pytest-mock pour simuler des fonctions.
def test_purchase_successful(mocker):
    """
    Teste un scénario d'achat réussi.
    On simule un utilisateur avec assez d'argent.
    """
    # 1. Préparation (Arrange)
    service = EconomyService()
    user_id = 123
    item_price = 100
    item_name = "test_item"

    # On crée un faux utilisateur que notre BDD simulée retournera.
    fake_user_data = {"user_id": user_id, "money": 500, "inventory": {"items": []}}

    # On simule `fetch_user` pour qu'il retourne notre faux utilisateur.
    mocker.patch("economy_service.fetch_user", return_value=fake_user_data)
    # On simule `save_user` pour vérifier qu'il est bien appelé.
    save_user_mock = mocker.patch("economy_service.save_user")

    # 2. Action (Act)
    updated_user = service.purchase(user_id, item_price, item_name)

    # 3. Vérification (Assert)
    # L'argent a-t-il été déduit ?
    assert updated_user["money"] == 400
    # L'objet a-t-il été ajouté à l'inventaire ?
    assert item_name in updated_user["inventory"]["items"]
    # La fonction de sauvegarde a-t-elle été appelée une seule fois ?
    save_user_mock.assert_called_once()


def test_purchase_insufficient_funds(mocker):
    """
    Teste un scénario d'achat échoué par manque de fonds.
    On simule un utilisateur sans assez d'argent.
    """
    # 1. Préparation (Arrange)
    service = EconomyService()
    user_id = 456
    item_price = 1000

    # Cet utilisateur n'a pas assez d'argent.
    fake_user_data = {"user_id": user_id, "money": 100, "inventory": {"items": []}}
    mocker.patch("economy_service.fetch_user", return_value=fake_user_data)
    save_user_mock = mocker.patch("economy_service.save_user")

    # 2. Action & 3. Vérification (Act & Assert)
    # On vérifie que l'exception `InsufficientFunds` est bien levée.
    with pytest.raises(InsufficientFunds):
        service.purchase(user_id, item_price, "expensive_item")

    # On vérifie que la sauvegarde n'a JAMAIS été appelée, car la transaction a échoué avant.
    save_user_mock.assert_not_called()
