"""Tests d'intégration pour les endpoints du serveur web Flask."""

from pathlib import Path
from typing import Any, Generator

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

# On importe l'app Flask et le module pour pouvoir le patcher
from cogs import web_cog
from cogs.web_cog import app


@pytest.fixture
def client(tmp_path: Path, mocker: MockerFixture) -> Generator[FlaskClient, None, None]:
    """Prépare un client de test Flask isolé.

    Args:
        tmp_path: Un chemin de dossier temporaire fourni par pytest.
        mocker: Le plugin pytest-mock.

    Yields:
        Un client de test Flask configuré.
    """
    # On simule la fonction de cache pour qu'elle ne dépende pas de la BDD.
    mocker.patch("cogs.web_cog.get_leaderboard_from_cache", return_value=[])

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_home_endpoint(client: FlaskClient):
    """Vérifie que l'endpoint '/' répond correctement."""
    # --- Action (Act) ---
    response = client.get("/")

    # --- Vérification (Assert) ---
    assert response.status_code == 200
    assert b"Bot is alive" in response.data


def test_leaderboard_endpoint(client: FlaskClient, mocker: MockerFixture):
    """Vérifie que l'endpoint '/leaderboard' affiche les données simulées.

    Args:
        client: Le client de test Flask.
        mocker: Le plugin pytest-mock.
    """
    # --- Préparation (Arrange) ---
    # On simule les données retournées par le cache du leaderboard.
    fake_leaderboard_data = [
        {"user_id": 1, "nick": "FooBar", "avatar": "", "xp": 42, "level": 3}
    ]
    mocker.patch(
        "cogs.web_cog.get_leaderboard_from_cache", return_value=fake_leaderboard_data
    )

    # --- Action (Act) ---
    response = client.get("/leaderboard")

    # --- Vérification (Assert) ---
    assert response.status_code == 200
    assert b"Leaderboard XP" in response.data
    assert b"FooBar" in response.data
    assert b"Niveau 3" in response.data
