import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_node(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts"))["texts"][0]
    nodes = [
        {"textId": text_id, "label": f"Node {n}", "level": 0, "position": n}
        for n in range(10)
    ]

    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)

    for node in nodes:
        resp = await test_client.post("/nodes", json=node, cookies=session_cookie)
        assert resp.status_code == 201, status_fail_msg(201, resp)


@pytest.mark.anyio
async def test_child_node_io(
    api_path,
    test_client: AsyncClient,
    get_sample_data,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts"))["texts"][0]
    node = get_sample_data("db/nodes.json", for_http=True)[0]

    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)

    # create parent
    resp = await test_client.post("/nodes", json=node, cookies=session_cookie)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    parent = resp.json()
    assert parent["id"]

    # create child
    child = node
    child["parentId"] = parent["id"]
    child["level"] = parent["level"] + 1
    child["position"] = 0
    resp = await test_client.post("/nodes", json=child, cookies=session_cookie)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    child = resp.json()
    assert "id" in resp.json()
    assert "parentId" in resp.json()
    assert resp.json()["parentId"] == str(child["parentId"])

    # find children by parent ID
    resp = await test_client.get(
        "/nodes", params={"textId": parent["textId"], "parentId": parent["id"]}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(child["id"])

    # find children by parent ID using dedicated children endpoint
    resp = await test_client.get(
        "/nodes/children",
        params={"parentId": child["parentId"]},
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(child["id"])

    # find children by text ID and null parent ID using dedicated children endpoint
    resp = await test_client.get(
        "/nodes/children", params={"textId": text_id}, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(parent["id"])


@pytest.mark.anyio
async def test_create_node_invalid_text_fail(
    api_path,
    test_client: AsyncClient,
    get_sample_data,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    await insert_sample_data("texts")
    node = get_sample_data("db/nodes.json", for_http=True)[0]
    node["textId"] = "5ed7cfba5e32eb7759a17565"

    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)

    resp = await test_client.post("/nodes", json=node, cookies=session_cookie)
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_get_nodes(
    api_path,
    test_client: AsyncClient,
    get_sample_data,
    insert_sample_data,
    status_fail_msg,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    nodes = get_sample_data("db/nodes.json", for_http=True)

    # test results length limit
    resp = await test_client.get(
        "/nodes", params={"textId": text_id, "level": 0, "limit": 2}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2

    # test empty results with status 200
    resp = await test_client.get(
        "/nodes", params={"textId": "5eb7cfb05e32e07750a1756a", "level": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # test results contain all nodes of level 0
    resp = await test_client.get("/nodes", params={"textId": text_id, "level": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == len(
        [n for n in nodes if n["textId"] == text_id and n["level"] == 0]
    )

    # test returned nodes have IDs
    assert "id" in resp.json()[0]
    # save node ID for later
    node_id = resp.json()[0]["id"]

    # test specific position
    resp = await test_client.get(
        "/nodes", params={"textId": text_id, "level": 0, "position": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1

    # test invalid request
    resp = await test_client.get("/nodes", params={"textId": text_id})
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # test get specific node by ID
    resp = await test_client.get(f"/nodes/{node_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == node_id


@pytest.mark.anyio
async def test_update_node(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes"))["texts"][0]
    # get node from db
    resp = await test_client.get("/nodes", params={"textId": text_id, "level": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    node = resp.json()[0]
    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)
    # update node
    node_update = {"label": "A fresh label"}
    resp = await test_client.patch(
        f"/nodes/{node['id']}", json=node_update, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(node["id"])
    assert "label" in resp.json()
    assert resp.json()["label"] == "A fresh label"
    # update unchanged node
    resp = await test_client.patch(
        f"/nodes/{node['id']}", json=node_update, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # update invalid node
    node_update = {"label": "Brand new label"}
    resp = await test_client.patch("/nodes/637b9ad396d541a505e5439b", json=node_update)
    assert resp.status_code == 400, status_fail_msg(400, resp, cookies=session_cookie)


@pytest.mark.anyio
async def test_delete_node(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes", "layers"))["texts"][0]

    # get node from db
    resp = await test_client.get(
        "/nodes", params={"textId": text_id, "level": 0, "position": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    node = resp.json()[0]

    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)

    # get existing layer
    resp = await test_client.get("/layers", params={"textId": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    layer = resp.json()[0]

    # create plaintext layer unit
    payload = {
        "layerId": layer["id"],
        "nodeId": node["id"],
        "text": "Ein Raabe geht im Feld spazieren.",
        "comment": "This is a comment",
    }
    resp = await test_client.post(
        "/units/plaintext", json=payload, cookies=session_cookie
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["text"] == payload["text"]
    assert resp.json()["comment"] == payload["comment"]
    assert "id" in resp.json()

    # delete node
    resp = await test_client.delete(f"/nodes/{node['id']}", cookies=session_cookie)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json().get("nodes", None) > 1
    assert resp.json().get("units", None) == 1


@pytest.mark.anyio
async def test_move_node(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts", "nodes", "layers"))["texts"][0]

    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)

    # get node from db
    resp = await test_client.get(
        "/nodes",
        params={"textId": text_id, "level": 0, "position": 0},
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    node = resp.json()[0]

    # move node
    resp = await test_client.post(
        f"/nodes/{node['id']}/move",
        json={"position": 1, "after": True, "parentId": None},
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["position"] == 1
