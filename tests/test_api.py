from textrig import __version__


def test_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}


def test_config(client):
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json()["app_name"] == "TextRig Test Instance"
    assert response.json()["db_uri"] == "mongodb://root:root@127.0.0.1:27017"
