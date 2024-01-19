import pytest

from httpx import AsyncClient
from tekst.models.node import NodeDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument


@pytest.mark.anyio
async def test_get_content_siblings(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, wrong_id, login
):
    await insert_sample_data("texts", "nodes", "resources", "contents")
    text = await TextDocument.find_one(TextDocument.slug == "pond")
    assert text
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.text_id == text.id, with_children=True
    )
    assert resource

    resp = await test_client.get(
        "/browse/content-siblings",
        params={"res": str(resource.id)},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3

    # wrong resource ID
    resp = await test_client.get(
        "/browse/content-siblings",
        params={"res": wrong_id},
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # siblings of resource version
    await login()
    resp = await test_client.post(
        f"/resources/{str(resource.id)}/version",
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()
    version_id = resp.json()["id"]
    resp = await test_client.get(
        "/browse/content-siblings",
        params={"res": version_id},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3


@pytest.mark.anyio
async def test_get_location_data(
    test_client: AsyncClient,
    insert_sample_data,
    get_sample_data,
    status_fail_msg,
    wrong_id,
):
    await insert_sample_data("texts", "nodes", "resources", "contents")
    texts = get_sample_data("db/texts.json", for_http=True)
    text_id = next((txt for txt in texts if len(txt["levels"]) == 2), {}).get("_id", "")
    assert len(text_id) > 0

    # get level 0 path
    resp = await test_client.get(
        "/browse/location-data",
        params={"txt": text_id, "lvl": 0, "pos": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["nodePath"]) > 0
    assert len(resp.json()["contents"]) == 0

    # higher level
    resp = await test_client.get(
        "/browse/location-data",
        params={"txt": text_id, "lvl": 1, "pos": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["nodePath"]) > 0
    assert len(resp.json()["contents"]) > 0

    # invalid node data
    resp = await test_client.get(
        "/browse/location-data",
        params={"txt": wrong_id, "lvl": 1, "pos": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["nodePath"]) == 0
    assert len(resp.json()["contents"]) == 0


@pytest.mark.anyio
async def test_get_path_options_by_head(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, wrong_id
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

    # invalid node data
    resp = await test_client.get(
        f"/browse/nodes/{wrong_id}/path/options-by-head",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_path_options_by_root(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, wrong_id
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

    # invalid node data
    resp = await test_client.get(
        f"/browse/nodes/{wrong_id}/path/options-by-root",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_resource_coverage_data(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources", "contents")
    resource_id = inserted_ids["resources"][0]
    resp = await test_client.get(
        f"/browse/resources/{resource_id}/coverage",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)

    # invalid node data
    resp = await test_client.get(
        f"/browse/resources/{wrong_id}/coverage",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_get_detailed_resource_coverage_data(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, wrong_id, login
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources", "contents")
    resource_id = inserted_ids["resources"][0]
    await login()

    # get detailed resource coverage data
    resp = await test_client.get(
        f"/browse/resources/{resource_id}/coverage-details",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)

    # fail with wrong resource ID
    resp = await test_client.get(
        f"/browse/resources/{wrong_id}/coverage-details",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)
