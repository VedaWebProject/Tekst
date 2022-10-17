from textrig import pkg_meta


def test_uidata(config, test_client):
    endpoint = f"{config.root_path}/uidata"
    response = test_client.get(endpoint)
    assert response.status_code == 200, f"Response of {endpoint} != 200"
    assert response.json()["platform"]["version"] == pkg_meta["version"]


def test_create_text(config, test_client):
    endpoint = f"{config.root_path}/texts"
    payload = {"title": "Just a Test"}
    resp = test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"RESP: {resp.status_code} ({resp.reason})"
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
