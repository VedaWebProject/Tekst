from textrig import pkg_meta


def test_uidata(app, client):
    endpoint = f"{app.root_path}/uidata"
    response = client.get(endpoint)
    assert response.status_code == 200, f"Response of {endpoint} != 200"
    assert response.json()["platform"]["version"] == pkg_meta["version"]
