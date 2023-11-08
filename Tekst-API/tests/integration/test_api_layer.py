import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_layer(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)
    payload = {
        "title": "A test layer",
        "textId": text_id,
        "description": "This is     a string with \n some space    chars",
        "level": 0,
        "layerType": "plaintext",
        "ownerId": user_data["id"],
    }

    resp = await test_client.post(
        "/layers/plaintext", json=payload, cookies=session_cookie
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()
    assert resp.json()["title"] == "A test layer"
    assert resp.json()["description"] == "This is a string with some space chars"
    assert resp.json()["ownerId"] == user_data.get("id")


@pytest.mark.anyio
async def test_create_layer_invalid(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    await insert_sample_data("texts", "nodes")
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)

    payload = {
        "title": "A test layer",
        "textId": "5eb7cfb05e32e07750a1756a",
        "level": 0,
        "layerType": "plaintext",
    }

    resp = await test_client.post(
        "/layers/plaintext", json=payload, cookies=session_cookie
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


# @pytest.mark.anyio
# async def test_get_layer_types_info(api_path, test_client: AsyncClient):
#     endpoint = f"/layers/types"
#     resp = await test_client.get(endpoint)
#     assert resp.status_code == 200, status_fail_msg(200, resp)
#     assert isinstance(resp.json(), dict)
#     assert len(resp.json()) == len(layer_type_manager.list_names())


@pytest.mark.anyio
async def test_update_layer(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes", "layers"))["texts"][0]
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)
    # create new layer (because only owner can update(write))
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "layerType": "plaintext",
        "ownerId": user_data.get("id"),
    }
    resp = await test_client.post(
        "/layers/plaintext", json=payload, cookies=session_cookie
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    layer_data = resp.json()
    assert "id" in layer_data
    assert "ownerId" in layer_data
    # update layer
    updates = {"title": "This Title Changed"}
    resp = await test_client.patch(
        f"/layers/{layer_data['layerType']}/{layer_data['id']}",
        json=updates,
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(layer_data["id"])
    assert resp.json()["title"] == updates["title"]


@pytest.mark.anyio
async def test_create_layer_with_forged_owner_id(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    user_data = await register_test_user()
    session_cookie = await get_session_cookie(user_data)
    # create new layer with made up owner ID
    payload = {
        "title": "Foo Bar Baz",
        "textId": text_id,
        "level": 0,
        "layerType": "plaintext",
        "ownerId": "643d3cdc21efd6c46ae1527e",
    }
    resp = await test_client.post(
        "/layers/plaintext", json=payload, cookies=session_cookie
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert resp.json()["ownerId"] != payload["ownerId"]


@pytest.mark.anyio
async def test_get_layer(
    api_path, test_client: AsyncClient, insert_sample_data, status_fail_msg
):
    text_id = (await insert_sample_data("texts", "nodes", "layers"))["texts"][0]
    # get existing layer id
    resp = await test_client.get("/layers", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]
    layer = resp.json()[0]
    layer_id = layer["id"]
    # get layer by id
    resp = await test_client.get(f"/layers/{layer_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == layer_id


@pytest.mark.anyio
async def test_access_private_layer(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "layers")
    text_id = inserted_ids["texts"][0]
    layer_id = inserted_ids["layers"][0]
    # get all accessible layers
    resp = await test_client.get("/layers", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    accessible_unauthorized = len(resp.json())
    # register test superuser
    user_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(user_data)
    # set layer to inactive
    resp = await test_client.patch(
        f"/layers/plaintext/{layer_id}", json={"public": False}, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["public"] is False
    # logout
    resp = await test_client.post("/auth/cookie/logout")
    assert resp.status_code == 204, status_fail_msg(204, resp)
    # get all accessible layers again, unauthorized
    resp = await test_client.get("/layers", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) < accessible_unauthorized  # this should be less now


@pytest.mark.anyio
async def test_get_layers(
    api_path, test_client: AsyncClient, insert_sample_data, status_fail_msg
):
    text_id = (await insert_sample_data("texts", "nodes", "layers"))["texts"][0]
    resp = await test_client.get(
        "/layers", params={"textId": text_id, "level": 1, "layerType": "plaintext"}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]

    layer_id = resp.json()[0]["id"]

    resp = await test_client.get(f"/layers/plaintext/{layer_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "layerType" in resp.json()

    # request invalid ID
    resp = await test_client.get("/layers/plaintext/foo")
    assert resp.status_code == 422, status_fail_msg(422, resp)


# @pytest.mark.anyio
# async def test_get_layer_template(
#     api_path, test_client: AsyncClient, insert_sample_data
# ):
#     await insert_sample_data("texts", "nodes", "layers")
#     # get all layers for text
#     endpoint = f"/layers"
#     resp = await test_client.get(endpoint, params={"textSlug": "rigveda"})
#     assert resp.status_code == 200, status_fail_msg(200, resp)
#     assert isinstance(resp.json(), list)
#     assert len(resp.json()) > 0
#     assert isinstance(resp.json()[0], dict)
#     assert "_id" in resp.json()[0]
#     layer_id = resp.json()[0]["_id"]  # remember layer ID
#     # get template for layer
#     endpoint = f"/layers/template"
#     resp = await test_client.get(endpoint, params={"layerId": layer_id})
#     assert resp.status_code == 200, status_fail_msg(200, resp)
#     assert isinstance(resp.json(), dict)
#     assert "_unitSchema" in resp.json()
#     assert "units" in resp.json()


# @pytest.mark.anyio
# async def test_get_layer_template_invalid_id(
#     api_path, test_client: AsyncClient, insert_sample_data
# ):
#     await insert_sample_data("texts", "nodes", "layers")
#     endpoint = f"/layers/template"
#     resp = await test_client.get(endpoint, params={"layerId": "foo"})
#     assert resp.status_code == 400, status_fail_msg(400, resp)
