import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_layer(
    root_path, test_client: AsyncClient, test_data, insert_test_data
):
    await insert_test_data("texts", "nodes")
    endpoint = f"{root_path}/layers/plaintext"
    payload = {
        "title": "A test layer",
        "textSlug": "rigveda",
        "description": "This is     a string with \n some space    chars",
        "level": 0,
        "layerType": "plaintext",
    }

    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"HTTP status {resp.status_code} (expected: 201)"
    assert "_id" in resp.json()
    assert resp.json()["title"] == "A test layer"
    assert resp.json()["description"] == "This is a string with some space chars"


@pytest.mark.anyio
async def test_create_layer_invalid(
    root_path, test_client: AsyncClient, test_data, insert_test_data
):
    await insert_test_data("texts", "nodes")
    endpoint = f"{root_path}/layers/plaintext"
    payload = {
        "title": "A test layer",
        "textSlug": "foo",
        "level": 0,
        "layerType": "plaintext",
    }

    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, f"HTTP status {resp.status_code} (expected: 400)"


# @pytest.mark.anyio
# async def test_get_layer_types_info(root_path, test_client: AsyncClient):
#     endpoint = f"{root_path}/layers/types"
#     resp = await test_client.get(endpoint)
#     assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
#     assert isinstance(resp.json(), dict)
#     assert len(resp.json()) == len(get_layer_type_names())


@pytest.mark.anyio
async def test_get_layer(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts", "nodes", "layers")
    # get existing layer id
    endpoint = f"{root_path}/layers"
    resp = await test_client.get(endpoint, params={"textSlug": "rigveda"})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "_id" in resp.json()[0]
    assert "layerType" in resp.json()[0]
    # update layer
    layer_update = resp.json()[0]
    layer_update["title"] = "foo bar baz"
    endpoint = f"{root_path}/layers/{layer_update['layerType']}"
    resp = await test_client.patch(endpoint, json=layer_update)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), dict)
    assert "_id" in resp.json()
    assert resp.json()["_id"] == str(layer_update["_id"])
    assert resp.json()["title"] == layer_update["title"]


@pytest.mark.anyio
async def test_update_layer(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts", "nodes", "layers")
    # get existing layer id
    endpoint = f"{root_path}/layers"
    resp = await test_client.get(endpoint, params={"textSlug": "rigveda"})
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "_id" in resp.json()[0]
    layer = resp.json()[0]
    layer_id = layer["_id"]
    # get layer by id
    endpoint = f"{root_path}/layers/{layer_id}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), dict)
    assert "_id" in resp.json()
    assert resp.json()["_id"] == layer_id


@pytest.mark.anyio
async def test_get_layers(root_path, test_client: AsyncClient, insert_test_data):
    await insert_test_data("texts", "nodes", "layers")
    endpoint = f"{root_path}/layers"
    resp = await test_client.get(
        endpoint, params={"textSlug": "rigveda", "level": 0, "layerType": "plaintext"}
    )
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "_id" in resp.json()[0]

    layer_id = resp.json()[0]["_id"]

    endpoint = f"{root_path}/layers/plaintext/{layer_id}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
    assert isinstance(resp.json(), dict)
    assert "layerType" in resp.json()

    # request invalid ID
    endpoint = f"{root_path}/layers/plaintext/foo"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 400, f"HTTP status {resp.status_code} (expected: 400)"


# @pytest.mark.anyio
# async def test_get_layer_template(
#     root_path, test_client: AsyncClient, insert_test_data
# ):
#     await insert_test_data("texts", "nodes", "layers")
#     # get all layers for text
#     endpoint = f"{root_path}/layers"
#     resp = await test_client.get(endpoint, params={"textSlug": "rigveda"})
#     assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
#     assert isinstance(resp.json(), list)
#     assert len(resp.json()) > 0
#     assert isinstance(resp.json()[0], dict)
#     assert "_id" in resp.json()[0]
#     layer_id = resp.json()[0]["_id"]  # remember layer ID
#     # get template for layer
#     endpoint = f"{root_path}/layers/template"
#     resp = await test_client.get(endpoint, params={"layerId": layer_id})
#     assert resp.status_code == 200, f"HTTP status {resp.status_code} (expected: 200)"
#     assert isinstance(resp.json(), dict)
#     assert "_unitSchema" in resp.json()
#     assert "units" in resp.json()


# @pytest.mark.anyio
# async def test_get_layer_template_invalid_id(
#     root_path, test_client: AsyncClient, insert_test_data
# ):
#     await insert_test_data("texts", "nodes", "layers")
#     endpoint = f"{root_path}/layers/template"
#     resp = await test_client.get(endpoint, params={"layerId": "foo"})
#     assert resp.status_code == 400, f"HTTP status {resp.status_code} (expected: 400)"
