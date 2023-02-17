import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_layer_unit(
    root_path, test_client: AsyncClient, insert_test_data, status_fail_msg
):
    text_id = await insert_test_data("texts", "nodes", "layers")
    # get ID of existing test layer
    endpoint = f"{root_path}/layers"
    resp = await test_client.get(
        endpoint, params={"textId": text_id, "layerType": "plaintext"}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    assert "id" in resp.json()[0]
    layer_id = resp.json()[0]["id"]

    # get ID of existing test node
    endpoint = f"{root_path}/nodes"
    resp = await test_client.get(endpoint, params={"textId": text_id, "level": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    assert "id" in resp.json()[0]
    node_id = resp.json()[0]["id"]

    # create plaintext layer unit
    endpoint = f"{root_path}/units/plaintext"
    payload = {
        "layerId": layer_id,
        "nodeId": node_id,
        "text": "Ein Raabe geht im Feld spazieren.",
        "meta": {"foo": "bar"},
    }
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert type(resp.json()) == dict
    assert resp.json()["text"] == "Ein Raabe geht im Feld spazieren."
    assert resp.json()["meta"]["foo"] == "bar"
    assert "id" in resp.json()
    unit_id = resp.json()["id"]

    # fail to create duplicate
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 409, status_fail_msg(409, resp)

    # get unit
    endpoint = f"{root_path}/units/plaintext/{unit_id}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == dict
    assert "id" in resp.json()
    assert resp.json()["text"] == "Ein Raabe geht im Feld spazieren."
    assert resp.json()["meta"]["foo"] == "bar"

    # fail to get unit with invalid ID
    endpoint = f"{root_path}/units/plaintext/637b9ad396d541a505e5439b"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # update unit
    endpoint = f"{root_path}/units/plaintext/{unit_id}"
    unit_update = {"text": "FOO BAR"}
    resp = await test_client.patch(endpoint, json=unit_update)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == dict
    assert "id" in resp.json()
    assert resp.json()["id"] == unit_id
    assert resp.json()["text"] == "FOO BAR"

    # fail to update unit with invalid ID
    unit_update = {"text": "FOO BAR"}
    endpoint = f"{root_path}/units/plaintext/637b9ad396d541a505e5439b"
    resp = await test_client.patch(endpoint, json=unit_update)
    assert resp.status_code == 400, status_fail_msg(400, resp)
