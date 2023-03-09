import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_node(
    root_path, test_client: AsyncClient, test_data, insert_test_data, status_fail_msg
):
    text_id = await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    nodes = [{"textId": text_id, **node} for node in test_data["nodes"]]

    for node in nodes:
        resp = await test_client.post(endpoint, json=node)
        assert resp.status_code == 201, status_fail_msg(201, resp)


@pytest.mark.anyio
async def test_child_node_io(
    root_path, test_client: AsyncClient, test_data, insert_test_data, status_fail_msg
):
    text_id = await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    node = {"textId": text_id, **test_data["nodes"][0]}

    # create parent
    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    parent = resp.json()
    assert parent["id"]

    # create child
    child = node
    child["parentId"] = parent["id"]
    child["level"] = parent["level"] + 1
    child["position"] = 0
    resp = await test_client.post(endpoint, json=child)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    child = resp.json()
    assert "id" in resp.json()
    assert "parentId" in resp.json()
    assert resp.json()["parentId"] == str(child["parentId"])

    # find children by parent ID
    resp = await test_client.get(
        endpoint, params={"textId": parent["textId"], "parentId": parent["id"]}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) is list
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(child["id"])

    # find children by parent ID using dedicated children endpoint
    resp = await test_client.get(f"{root_path}/nodes/{child['parentId']}/children")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) is list
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(child["id"])


@pytest.mark.anyio
async def test_create_node_invalid_text_fail(
    root_path, test_client: AsyncClient, test_data, insert_test_data, status_fail_msg
):
    await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]
    node["textId"] = "5eb7cfb05e32e07750a1756a"

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_create_node_duplicate_fail(
    root_path, test_client: AsyncClient, test_data, insert_test_data, status_fail_msg
):
    text_id = await insert_test_data("texts")
    endpoint = f"{root_path}/nodes"
    node = test_data["nodes"][0]
    node["textId"] = text_id

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 201, status_fail_msg(201, resp)

    resp = await test_client.post(endpoint, json=node)
    assert resp.status_code == 409, status_fail_msg(409, resp)


@pytest.mark.anyio
async def test_get_nodes(
    root_path, test_client: AsyncClient, test_data, insert_test_data, status_fail_msg
):
    text_id = await insert_test_data("texts", "nodes")
    endpoint = f"{root_path}/nodes"
    nodes = test_data["nodes"]

    # test results length limit
    resp = await test_client.get(
        endpoint, params={"textId": text_id, "level": 0, "limit": 2}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) is list
    assert len(resp.json()) == 2

    # test empty results with status 200
    resp = await test_client.get(
        endpoint, params={"textId": "5eb7cfb05e32e07750a1756a", "level": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) is list
    assert len(resp.json()) == 0

    # test results contain all nodes of level 0
    resp = await test_client.get(endpoint, params={"textId": text_id, "level": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) is list
    assert len(resp.json()) == len(nodes)

    # test returned nodes have IDs
    assert "id" in resp.json()[0]
    # save node ID for later
    node_id = resp.json()[0]["id"]

    # test specific position
    resp = await test_client.get(
        endpoint, params={"textId": text_id, "level": 0, "position": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) is list
    assert len(resp.json()) == 1

    # test invalid request
    resp = await test_client.get(endpoint, params={"textId": text_id})
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # test get specific node by ID
    resp = await test_client.get(f"{endpoint}/{node_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == node_id


@pytest.mark.anyio
async def test_update_node(
    root_path, test_client: AsyncClient, insert_test_data, test_data, status_fail_msg
):
    text_id = await insert_test_data("texts", "nodes")
    # get node from db
    endpoint = f"{root_path}/nodes"
    resp = await test_client.get(endpoint, params={"textId": text_id, "level": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    node = resp.json()[0]
    # update node
    endpoint = f"{root_path}/nodes/{node['id']}"
    node_update = {"label": "A fresh label"}
    resp = await test_client.patch(endpoint, json=node_update)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(node["id"])
    assert "label" in resp.json()
    assert resp.json()["label"] == "A fresh label"
    # update unchanged node
    resp = await test_client.patch(endpoint, json=node_update)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # update invalid node
    node_update = {"label": "Brand new label"}
    endpoint = f"{root_path}/nodes/637b9ad396d541a505e5439b"
    resp = await test_client.patch(endpoint, json=node_update)
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_node_next(
    root_path, test_client: AsyncClient, insert_test_data, test_data, status_fail_msg
):
    text_id = await insert_test_data("texts", "nodes")
    # get second last node from level 0
    endpoint = f"{root_path}/nodes"
    resp = await test_client.get(endpoint, params={"textId": text_id, "level": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == list
    assert len(resp.json()) > 0
    nodes = resp.json()
    node_second_last = nodes[len(nodes) - 2]
    node_last = nodes[len(nodes) - 1]
    # get next node
    endpoint = f"{root_path}/nodes/{node_second_last['id']}/next"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert type(resp.json()) == dict
    assert "id" in resp.json()
    assert resp.json()["id"] == str(node_last["id"])
    # fail to get node after last
    endpoint = f"{root_path}/nodes/{node_last['id']}/next"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 404, status_fail_msg(404, resp)
