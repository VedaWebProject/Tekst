from fastapi.testclient import TestClient
from textrig import __version__
from textrig.main import app
from textrig.settings import Settings, get_settings

client = TestClient(app)


# override settings for tests
def get_cfg_override():
    return Settings(app_name="suppe")


app.dependency_overrides[get_settings] = get_cfg_override


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}


def test_settings():
    response = client.get("/settings")
    assert response.status_code == 200
    assert response.json()["app_name"] == "suppe"
