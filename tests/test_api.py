from textrig import pkg_meta


def test_meta(app, client):
    endpoint = f"{app.root_path}/meta"
    response = client.get(endpoint)
    assert response.status_code == 200, f"Response of {endpoint} != 200"
    assert response.json()["version"] == pkg_meta["version"]
