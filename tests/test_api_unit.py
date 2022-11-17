import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_layer_unit(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts", "nodes", "layers")
    # get ID of existing test layer
    endpoint = f"{root_path}/layer"
    resp = await test_client.get(
        endpoint, params={"text_slug": "rigveda", "layer_type": "fulltext"}
    )
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    assert "id" in resp.json()[0]
    node_id = resp.json()[0]["id"]

    # get ID of existing test node
    endpoint = f"{root_path}/node"
    resp = await test_client.get(endpoint, params={"text_slug": "rigveda", "level": 0})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    assert "id" in resp.json()[0]
    layer_id = resp.json()[0]["id"]

    # create fulltext layer unit
    endpoint = f"{root_path}/unit/fulltext"
    payload = {
        "layerId": layer_id,
        "nodeId": node_id,
        "text": "Ein Raabe geht im Feld spazieren.",
        "meta": {"foo": "bar"},
    }
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"HTTP status {resp.status_code} (expected: 201)"
    assert type(resp.json()) == dict
    assert resp.json()["text"] == "Ein Raabe geht im Feld spazieren."
    assert resp.json()["meta"]["foo"] == "bar"
    assert "id" in resp.json()
    unit_id = resp.json()["id"]

    # get unit
    endpoint = f"{root_path}/unit/fulltext"
    resp = await test_client.get(endpoint, params={"unit_id": unit_id})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == dict
    assert "id" in resp.json()
    assert resp.json()["text"] == "Ein Raabe geht im Feld spazieren."
    assert resp.json()["meta"]["foo"] == "bar"

    # update unit
    # TODO
