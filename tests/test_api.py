from textrig import pkg_meta


def test_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": pkg_meta["version"]}


def test_config(client):
    response = client.get("/config")
    assert response.status_code == 200
    assert response.json()["app_name"] == "TextRig Test Instance"
