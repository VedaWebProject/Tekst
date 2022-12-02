import pytest
from httpx import AsyncClient
from textrig.layer_types import get_layer_type


@pytest.mark.anyio
async def test_create_layer_unit(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts", "nodes", "layers")
    # get ID of existing test layer
    endpoint = f"{root_path}/layers"
    resp = await test_client.get(
        endpoint, params={"text_slug": "rigveda", "layer_type": "fulltext"}
    )
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    assert "id" in resp.json()[0]
    node_id = resp.json()[0]["id"]

    # get ID of existing test node
    endpoint = f"{root_path}/nodes"
    resp = await test_client.get(endpoint, params={"text_slug": "rigveda", "level": 0})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    assert "id" in resp.json()[0]
    layer_id = resp.json()[0]["id"]

    # create fulltext layer unit
    endpoint = f"{root_path}/units/fulltext"
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

    # fail to create duplicate
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 409, f"HTTP status {resp.status_code} (expected: 409)"

    # get unit
    endpoint = f"{root_path}/units/fulltext/{unit_id}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == dict
    assert "id" in resp.json()
    assert resp.json()["text"] == "Ein Raabe geht im Feld spazieren."
    assert resp.json()["meta"]["foo"] == "bar"

    # fail to get unit with invalid ID
    endpoint = f"{root_path}/units/fulltext/637b9ad396d541a505e5439b"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 404, f"HTTP status {resp.status_code} (expected: 404)"

    # update unit
    endpoint = f"{root_path}/units/fulltext"
    UpdateModel = get_layer_type("fulltext").get_unit_update_model()
    unit_update = UpdateModel(id=unit_id, text="FOO BAR")
    resp = await test_client.patch(endpoint, json=unit_update.dict())
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert type(resp.json()) == dict
    assert "id" in resp.json()
    assert resp.json()["id"] == unit_id
    assert resp.json()["text"] == "FOO BAR"

    # fail to update unit with invalid ID
    unit_update = UpdateModel(id="637b9ad396d541a505e5439b", text="FOO BAR")
    resp = await test_client.patch(endpoint, json=unit_update.dict())
    assert resp.status_code == 400, f"HTTP status {resp.status_code} (expected: 400)"
