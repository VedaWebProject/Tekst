import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_texts(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts")
    endpoint = f"{root_path}/texts"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    text_id = resp.json()[0]["id"]
    # get one by specific id
    resp = await test_client.get(f"{endpoint}/{text_id}")
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert type(resp.json()) == dict
    assert resp.json()["id"] == text_id
    # get one by non-existent id
    resp = await test_client.get(f"{endpoint}/637b9ad396d541a505e5439b")
    assert resp.status_code == 404, f"HTTP {resp.status_code} != 404 ({resp.json()})"


@pytest.mark.anyio
async def test_create_text(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/texts"
    payload = {"title": "Just a Test", "slug": "justatest", "levels": ["foo"]}
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"HTTP {resp.status_code} != 201 ({resp.json()})"
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
    # create duplicate
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 409, f"HTTP {resp.status_code} != 409 ({resp.json()})"


@pytest.mark.anyio
async def test_update_text(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts")
    # get text from db
    endpoint = f"{root_path}/texts"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    text = resp.json()[0]
    # update text
    text_update = {"id": text["id"], "title": "Another text"}
    resp = await test_client.patch(endpoint, json=text_update)
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert "id" in resp.json()
    assert resp.json()["id"] == str(text["id"])
    assert "title" in resp.json()
    assert resp.json()["title"] == "Another text"
    # update unchanged text
    resp = await test_client.patch(endpoint, json=text_update)
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    # update invalid text
    text_update = {"id": "637b9ad396d541a505e5439b", "title": "Yet another text"}
    resp = await test_client.patch(endpoint, json=text_update)
    assert resp.status_code == 400, f"HTTP {resp.status_code} != 400 ({resp.json()})"
