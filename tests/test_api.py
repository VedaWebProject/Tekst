from textrig import pkg_meta


def test_meta(app, client):
    response = client.get(f"{app.root_path}/meta")
    assert response.status_code == 200
    assert response.json()["version"] == pkg_meta["version"]
