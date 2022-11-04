import pytest
from httpx import AsyncClient
from textrig import pkg_meta


@pytest.mark.anyio
async def test_uidata(config, test_client: AsyncClient):
    endpoint = f"{config.root_path}/uidata"
    response = await test_client.get(endpoint)
    assert response.status_code == 200, f"Response of {endpoint} != 200"
    assert response.json()["platform"]["version"] == pkg_meta["version"]


@pytest.mark.anyio
async def test_get_texts(config, test_client: AsyncClient):
    endpoint = f"{config.root_path}/texts"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"RESP: {resp.status_code} ({resp.reason})"
    assert resp.json() == []


@pytest.mark.anyio
async def test_create_text(config, test_client: AsyncClient):
    endpoint = f"{config.root_path}/texts"
    payload = {"title": "Just a Test"}
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"RESP: {resp.status_code} ({resp.reason})"
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
