import pytest
from httpx import AsyncClient
from textrig.layer_types import get_layer_type_names


@pytest.mark.anyio
async def test_create_fulltext_layer(
    root_path, test_client: AsyncClient, test_data, load_test_data_nodes
):
    endpoint = f"{root_path}/layer"
    payload = {
        "title": "A test layer",
        "textSlug": "rigveda",
        "level": 0,
        "layer_type": "fulltext",
    }

    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"HTTP status {resp.status_code} (expected: 201)"
    assert "id" in resp.json()
    assert resp.json()["title"] == "A test layer"


@pytest.mark.anyio
async def test_get_layer_types_info(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/layer/types"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), dict)
    assert len(resp.json()) == len(get_layer_type_names())


@pytest.mark.anyio
async def test_get_layers(root_path, test_client: AsyncClient, load_test_data_layers):
    endpoint = f"{root_path}/layer"
    resp = await test_client.get(endpoint, params={"text_slug": "rigveda"})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]
    layer_id = resp.json()[0]["id"]
    endpoint = f"{root_path}/layer/{layer_id}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), dict)
    assert "layerType" in resp.json()


@pytest.mark.anyio
async def test_get_layer_template(
    root_path, test_client: AsyncClient, load_test_data_layers
):
    endpoint = f"{root_path}/layer"
    resp = await test_client.get(endpoint, params={"text_slug": "rigveda"})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]
    layer_id = resp.json()[0]["id"]
    endpoint = f"{root_path}/layer/template"
    resp = await test_client.get(endpoint, params={"layer_id": layer_id})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), dict)
    assert "_unitSchema" in resp.json()
    assert "units" in resp.json()
