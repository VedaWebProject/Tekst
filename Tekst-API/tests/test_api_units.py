import pytest

from httpx import AsyncClient
from tekst.models.node import NodeDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.unit import UnitBaseDocument


@pytest.mark.anyio
async def test_create_unit(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    await insert_sample_data("texts", "nodes", "resources")
    resource = await ResourceBaseDocument.find_one(with_children=True)
    node = await NodeDocument.find_one(NodeDocument.level == resource.level)
    await login(is_superuser=True)

    # create plaintext resource unit
    unit_create_data = {
        "resourceId": str(resource.id),
        "resourceType": "plaintext",
        "nodeId": str(node.id),
        "text": "Ein Raabe geht im Feld spazieren.",
        "comment": "This is a comment",
    }
    resp = await test_client.post(
        "/units",
        json=unit_create_data,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["text"] == unit_create_data["text"]
    assert resp.json()["comment"] == unit_create_data["comment"]
    assert "id" in resp.json()

    # fail to create duplicate
    resp = await test_client.post(
        "/units",
        json=unit_create_data,
    )
    assert resp.status_code == 409, status_fail_msg(409, resp)

    # fail to create unit for resource we don't have write access to
    await login(is_superuser=False)
    resp = await test_client.post(
        "/units",
        json=unit_create_data,
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)


@pytest.mark.anyio
async def test_get_unit(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources", "units")
    unit_id = inserted_ids["units"][0]
    await login(is_superuser=True)

    # get unit by ID
    resp = await test_client.get(
        f"/units/{unit_id}",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == unit_id

    # fail to get unit with wrong ID
    resp = await test_client.get(
        f"/units/{wrong_id}",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # find all units
    resp = await test_client.get(
        "/units",
        params={"limit": 100},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0


@pytest.mark.anyio
async def test_update_unit(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    await insert_sample_data("texts", "nodes", "resources", "units")
    resource = await ResourceBaseDocument.find_one(with_children=True)
    unit = await UnitBaseDocument.find_one(
        UnitBaseDocument.resource_id == resource.id, with_children=True
    )
    await login(is_superuser=True)

    # update unit
    resp = await test_client.patch(
        f"/units/{str(unit.id)}",
        json={"resourceType": "plaintext", "text": "FOO BAR"},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(unit.id)
    assert resp.json()["text"] == "FOO BAR"

    # fail to update unit with wrong ID
    resp = await test_client.patch(
        f"/units/{wrong_id}",
        json={"resourceType": "plaintext", "text": "FOO BAR"},
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # fail to update unit with changed resource ID
    resp = await test_client.patch(
        f"/units/{str(unit.id)}",
        json={
            "resourceType": "plaintext",
            "text": "FOO BAR",
            "resourceId": wrong_id,
        },
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # fail to update unit with bogus resource type
    resp = await test_client.patch(
        f"/units/{str(unit.id)}",
        json={
            "resourceType": "bogus",
            "text": "FOO BAR",
            "resourceId": str(resource.id),
        },
    )
    assert resp.status_code == 422, status_fail_msg(422, resp)

    # fail to update unit with changed resource type
    resp = await test_client.patch(
        f"/units/{str(unit.id)}",
        json={
            "resourceType": "debug",
            "text": "FOO BAR",
            "resourceId": str(resource.id),
        },
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # fail to update unit of resource we don't have write access to
    await login(is_superuser=False)
    node = await NodeDocument.find_one(NodeDocument.level == resource.level)
    resp = await test_client.patch(
        f"/units/{str(unit.id)}",
        json={
            "resourceId": str(resource.id),
            "nodeId": str(node.id),
            "resourceType": "plaintext",
            "text": "FOO BAR",
        },
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)


@pytest.mark.anyio
async def test_delete_unit(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "nodes", "resources", "units")
    unit_id = inserted_ids["units"][0]
    superuser = await login(is_superuser=True)

    # fail to delete with wrong ID
    resp = await test_client.delete(
        f"/units/{wrong_id}",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # fail to delete without write access
    await login(is_superuser=False)
    resp = await test_client.delete(
        f"/units/{unit_id}",
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)

    # delete unit
    await login(user=superuser)
    resp = await test_client.delete(
        f"/units/{unit_id}",
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)
