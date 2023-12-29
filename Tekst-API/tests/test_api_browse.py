import pytest

from httpx import AsyncClient
from tekst.models.node import NodeDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument


@pytest.mark.anyio
async def test_get_unit_siblings(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
):
    await insert_sample_data("texts", "nodes", "resources", "units")
    text = await TextDocument.find_one(TextDocument.slug == "pond")
    assert text
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.text_id == text.id, with_children=True
    )
    assert resource

    resp = await test_client.get(
        "/browse/unit-siblings",
        params={"resourceId": str(resource.id)},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3

    # invalid resource ID
    resp = await test_client.get(
        "/browse/unit-siblings",
        params={"resourceId": "658c163106aa5002b5b90e33"},
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_get_node_path(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
):
    inserted_ids = await insert_sample_data("texts", "nodes")
    text_id = inserted_ids["texts"][0]
    resp = await test_client.get(
        "/browse/nodes/path",
        params={"textId": text_id, "level": 0, "position": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0

    # higher level
    resp = await test_client.get(
        "/browse/nodes/path",
        params={"textId": text_id, "level": 1, "position": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0

    # invalid node data
    resp = await test_client.get(
        "/browse/nodes/path",
        params={"textId": "658c163106aa5002b5b90e33", "level": 0, "position": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_path_options_by_head(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
):
    await insert_sample_data("texts", "nodes")
    text = await TextDocument.find_one(TextDocument.slug == "fdhdgg")
    node = await NodeDocument.find_one(
        NodeDocument.text_id == text.id, NodeDocument.level == 1
    )
    resp = await test_client.get(
        f"/browse/nodes/{str(node.id)}/path/options-by-head",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert isinstance(resp.json()[0], list)


@pytest.mark.anyio
async def test_get_path_options_by_root(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
):
    await insert_sample_data("texts", "nodes")
    text = await TextDocument.find_one(TextDocument.slug == "fdhdgg")
    node = await NodeDocument.find_one(
        NodeDocument.text_id == text.id, NodeDocument.level == 0
    )
    resp = await test_client.get(
        f"/browse/nodes/{str(node.id)}/path/options-by-root",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert isinstance(resp.json()[0], list)


@pytest.mark.anyio
async def test_get_resource_coverage_data(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources", "units")
    resource_id = inserted_ids["resources"][0]
    resp = await test_client.get(
        f"/browse/resources/{resource_id}/coverage",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
