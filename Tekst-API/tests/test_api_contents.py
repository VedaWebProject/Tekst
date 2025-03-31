import pytest

from httpx import AsyncClient
from tekst.models.content import ContentBaseDocument
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument


@pytest.mark.anyio
async def test_create_content(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
):
    await insert_test_data("texts", "locations", "resources")
    resource = await ResourceBaseDocument.find_one(with_children=True)
    assert resource.resource_type == "plainText"
    location = await LocationDocument.find_one(LocationDocument.level == resource.level)
    await login(is_superuser=True)

    # create plain text resource content
    content_create_data = {
        "resourceId": str(resource.id),
        "resourceType": "plainText",
        "locationId": str(location.id),
        "text": "Ein Raabe geht im Feld spazieren.",
        "comment": "This is a comment",
    }

    # fail to create content with invalid resource type
    invalid_content_create_data = dict(**content_create_data)
    invalid_content_create_data["resourceType"] = "foo"
    resp = await test_client.post(
        "/contents",
        json=invalid_content_create_data,
    )
    assert_status(422, resp)

    # fail to create content with resource type not matching resource
    invalid_content_create_data = dict(**content_create_data)
    invalid_content_create_data["resourceType"] = "richText"
    invalid_content_create_data["html"] = "<p>foo</p>"
    resp = await test_client.post(
        "/contents",
        json=invalid_content_create_data,
    )
    assert_status(400, resp)

    # successfully create content
    resp = await test_client.post(
        "/contents",
        json=content_create_data,
    )
    assert_status(201, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["text"] == content_create_data["text"]
    assert resp.json()["comment"] == content_create_data["comment"]
    assert "id" in resp.json()

    # fail to create duplicate
    resp = await test_client.post(
        "/contents",
        json=content_create_data,
    )
    assert_status(409, resp)

    # fail to create content for resource we don't have write access to
    await login(is_superuser=False)
    resp = await test_client.post(
        "/contents",
        json=content_create_data,
    )
    assert_status(403, resp)


@pytest.mark.anyio
async def test_get_content(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources", "contents")
    content_id = inserted_ids["contents"][0]
    await login(is_superuser=True)

    # get content by ID
    resp = await test_client.get(
        f"/contents/{content_id}",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == content_id

    # fail to get content with wrong ID
    resp = await test_client.get(
        f"/contents/{wrong_id}",
    )
    assert_status(404, resp)


@pytest.mark.anyio
async def test_find_contents(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    resource_id = (
        await insert_test_data("texts", "locations", "resources", "contents")
    )["resources"][0]
    await login(is_superuser=True)

    # find all contents
    resp = await test_client.get(
        "/contents",
        params={"res": [resource_id], "limit": 100},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0

    # find all contents of resource
    resp = await test_client.get(
        "/contents",
        params={"limit": 100},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0


@pytest.mark.anyio
async def test_update_content(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    await insert_test_data("texts", "locations", "resources", "contents")
    resource = await ResourceBaseDocument.find_one(with_children=True)
    content = await ContentBaseDocument.find_one(
        ContentBaseDocument.resource_id == resource.id, with_children=True
    )
    await login(is_superuser=True)

    # update content
    resp = await test_client.patch(
        f"/contents/{str(content.id)}",
        json={"resourceType": "plainText", "text": "FOO BAR"},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(content.id)
    assert resp.json()["text"] == "FOO BAR"

    # update content w/ empty comment and note strings
    resp = await test_client.patch(
        f"/contents/{str(content.id)}",
        json={"resourceType": "plainText", "comment": "", "notes": ""},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["comment"] is None
    assert resp.json()["notes"] is None

    # update content w/ None as comment and note
    resp = await test_client.patch(
        f"/contents/{str(content.id)}",
        json={"resourceType": "plainText", "comment": None, "notes": None},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["comment"] is None
    assert resp.json()["notes"] is None

    # fail to update content with wrong ID
    resp = await test_client.patch(
        f"/contents/{wrong_id}",
        json={"resourceType": "plainText", "text": "FOO BAR"},
    )
    assert_status(404, resp)

    # fail to update content with bogus resource type
    resp = await test_client.patch(
        f"/contents/{str(content.id)}",
        json={
            "resourceType": "bogus",
            "text": "FOO BAR",
        },
    )
    assert_status(422, resp)

    # fail to update content of resource we don't have write access to
    await login(is_superuser=False)
    location = await LocationDocument.find_one(LocationDocument.level == resource.level)
    resp = await test_client.patch(
        f"/contents/{str(content.id)}",
        json={
            "resourceId": str(resource.id),
            "locationId": str(location.id),
            "resourceType": "plainText",
            "text": "FOO BAR",
        },
    )
    assert_status(403, resp)


@pytest.mark.anyio
async def test_delete_content(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources", "contents")
    content_id = inserted_ids["contents"][0]
    superuser = await login(is_superuser=True)

    # fail to delete with wrong ID
    resp = await test_client.delete(
        f"/contents/{wrong_id}",
    )
    assert_status(404, resp)

    # fail to delete without write access
    await login(is_superuser=False)
    resp = await test_client.delete(
        f"/contents/{content_id}",
    )
    assert_status(403, resp)

    # delete content
    await login(user=superuser)
    resp = await test_client.delete(
        f"/contents/{content_id}",
    )
    assert_status(204, resp)
