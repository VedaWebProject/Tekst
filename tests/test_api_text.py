import pytest
from httpx import AsyncClient
from textrig.models.text import TextRead, TextUpdate


@pytest.mark.anyio
async def test_get_texts(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts")
    endpoint = f"{root_path}/text"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0


@pytest.mark.anyio
async def test_create_text(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/text"
    payload = {"title": "Just a Test"}
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"HTTP status {resp.status_code} (expected: 201)"
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"


@pytest.mark.anyio
async def test_update_text(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts")
    # get text from db
    endpoint = f"{root_path}/text"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    text = TextRead(**resp.json()[0])
    # update text
    text_update = TextUpdate(id=text.id, title="Another text")
    resp = await test_client.patch(endpoint, json=text_update.dict())
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert "id" in resp.json()
    assert resp.json()["id"] == str(text.id)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Another text"
