import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_layer(
    api_path,
    test_client: AsyncClient,
    test_data,
    insert_test_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = await insert_test_data("texts", "nodes")
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)
    endpoint = f"{api_path}/layers/plaintext"
    payload = {
        "title": "A test layer",
        "textId": text_id,
        "description": "This is     a string with \n some space    chars",
        "level": 0,
        "layerType": "plaintext",
        "ownerId": user_data["id"],
    }

    resp = await test_client.post(endpoint, json=payload, cookies=session_cookie)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()
    assert resp.json()["title"] == "A test layer"
    assert resp.json()["description"] == "This is a string with some space chars"
    assert resp.json()["ownerId"] == user_data.get("id")


@pytest.mark.anyio
async def test_create_layer_invalid(
    api_path,
    test_client: AsyncClient,
    test_data,
    insert_test_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    await insert_test_data("texts", "nodes")
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)

    endpoint = f"{api_path}/layers/plaintext"
    payload = {
        "title": "A test layer",
        "textId": "5eb7cfb05e32e07750a1756a",
        "level": 0,
        "layerType": "plaintext",
    }

    resp = await test_client.post(endpoint, json=payload, cookies=session_cookie)
    assert resp.status_code == 400, status_fail_msg(400, resp)


# @pytest.mark.anyio
# async def test_get_layer_types_info(api_path, test_client: AsyncClient):
#     endpoint = f"{api_path}/layers/types"
#     resp = await test_client.get(endpoint)
#     assert resp.status_code == 200, status_fail_msg(200, resp)
#     assert isinstance(resp.json(), dict)
#     assert len(resp.json()) == len(get_layer_type_names())


@pytest.mark.anyio
async def test_update_layer(
    api_path,
    test_client: AsyncClient,
    insert_test_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = await insert_test_data("texts", "nodes", "layers")
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)
    # create new layer (because only owner can update(write))
    endpoint = f"{api_path}/layers/plaintext"
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "layerType": "plaintext",
        "ownerId": user_data.get("id"),
    }
    resp = await test_client.post(endpoint, json=payload, cookies=session_cookie)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    layer_data = resp.json()
    assert "id" in layer_data
    assert "ownerId" in layer_data
    # update layer
    updates = {"title": "This Title Changed"}
    endpoint = f"{api_path}/layers/{layer_data['layerType']}/{layer_data['id']}"
    resp = await test_client.patch(endpoint, json=updates, cookies=session_cookie)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(layer_data["id"])
    assert resp.json()["title"] == updates["title"]


@pytest.mark.anyio
async def test_get_layer(
    api_path, test_client: AsyncClient, insert_test_data, status_fail_msg
):
    text_id = await insert_test_data("texts", "nodes", "layers")
    # get existing layer id
    endpoint = f"{api_path}/layers"
    resp = await test_client.get(endpoint, params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]
    layer = resp.json()[0]
    layer_id = layer["id"]
    # get layer by id
    endpoint = f"{api_path}/layers/{layer_id}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == layer_id


@pytest.mark.anyio
async def test_get_layers(
    api_path, test_client: AsyncClient, insert_test_data, status_fail_msg
):
    text_id = await insert_test_data("texts", "nodes", "layers")
    endpoint = f"{api_path}/layers"
    resp = await test_client.get(
        endpoint, params={"textId": text_id, "level": 0, "layerType": "plaintext"}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]

    layer_id = resp.json()[0]["id"]

    endpoint = f"{api_path}/layers/plaintext/{layer_id}"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "layerType" in resp.json()

    # request invalid ID
    endpoint = f"{api_path}/layers/plaintext/foo"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 422, status_fail_msg(422, resp)


# @pytest.mark.anyio
# async def test_get_layer_template(
#     api_path, test_client: AsyncClient, insert_test_data
# ):
#     await insert_test_data("texts", "nodes", "layers")
#     # get all layers for text
#     endpoint = f"{api_path}/layers"
#     resp = await test_client.get(endpoint, params={"textSlug": "rigveda"})
#     assert resp.status_code == 200, status_fail_msg(200, resp)
#     assert isinstance(resp.json(), list)
#     assert len(resp.json()) > 0
#     assert isinstance(resp.json()[0], dict)
#     assert "_id" in resp.json()[0]
#     layer_id = resp.json()[0]["_id"]  # remember layer ID
#     # get template for layer
#     endpoint = f"{api_path}/layers/template"
#     resp = await test_client.get(endpoint, params={"layerId": layer_id})
#     assert resp.status_code == 200, status_fail_msg(200, resp)
#     assert isinstance(resp.json(), dict)
#     assert "_unitSchema" in resp.json()
#     assert "units" in resp.json()


# @pytest.mark.anyio
# async def test_get_layer_template_invalid_id(
#     api_path, test_client: AsyncClient, insert_test_data
# ):
#     await insert_test_data("texts", "nodes", "layers")
#     endpoint = f"{api_path}/layers/template"
#     resp = await test_client.get(endpoint, params={"layerId": "foo"})
#     assert resp.status_code == 400, status_fail_msg(400, resp)
