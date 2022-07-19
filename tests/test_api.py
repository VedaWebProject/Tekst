from fastapi.testclient import TestClient
from textrig import __version__
from textrig.main import app

client = TestClient(app)


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}
