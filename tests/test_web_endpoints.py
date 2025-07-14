import pytest
from cogs.web_cog import app  # On importe l'app Flask depuis cogs.web_cog
import cogs.web_cog as web_module  # Pour pouvoir patcher get_leaderboard_from_cache


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Prépare un client de test Flask isolé dans tmp_path,
    avec un fichier bot.log factice.
    """
    # 1) Change le répertoire de travail vers tmp_path
    monkeypatch.chdir(tmp_path)

    # 2) Crée un bot.log avec un contenu identifiable
    log_file = tmp_path / "bot.log"
    log_file.write_text("Contenu test des logs")

    # 3) Active le mode testing et retourne le client
    app.testing = True
    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    """
    L'endpoint '/' doit répondre 200 et contenir 'Bot is alive'.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Bot is alive" in resp.data


def test_logs_endpoint(client):
    """
    L'endpoint '/logs' doit renvoyer le contenu de bot.log.
    """
    resp = client.get("/logs")
    assert resp.status_code == 200
    assert b"Contenu test des logs" in resp.data


def test_leaderboard_endpoint(client, monkeypatch):
    """
    L'endpoint '/leaderboard' doit répondre 200 et afficher
    le titre 'Leaderboard XP', le pseudo et le niveau de l'entrée simulée.
    """
    # On patch directement dans cogs.web_cog la fonction utilisée pour le cache
    monkeypatch.setattr(
        web_module,
        "get_leaderboard_from_cache",
        lambda: [{"user_id": 1, "nick": "FooBar", "avatar": "", "xp": 42, "level": 3}],
    )

    resp = client.get("/leaderboard")
    assert resp.status_code == 200

    # Vérifie la présence du titre, du pseudo et du niveau dans la page
    assert b"Leaderboard XP" in resp.data
    assert b"FooBar" in resp.data
    assert b"Niveau 3" in resp.data
