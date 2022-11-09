import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_texts(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/text"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"response status {resp.status_code} != 200"
    assert resp.json() == []


@pytest.mark.anyio
async def test_create_text(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/text"
    payload = {"title": "Just a Test"}
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"response status {resp.status_code} != 201"
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
