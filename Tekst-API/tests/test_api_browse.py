import pytest

from httpx import AsyncClient
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument


@pytest.mark.anyio
async def test_get_content_context(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    wrong_id,
    login,
):
    await insert_test_data("texts", "locations", "resources", "contents")
    text = await TextDocument.find_one(TextDocument.slug == "foo")
    assert text
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.text_id == text.id, with_children=True
    )
    assert resource
    location = await LocationDocument.find_one(
        LocationDocument.level == resource.level,
        LocationDocument.text_id == resource.text_id,
    )
    assert location

    resp = await test_client.get(
        "/browse/context",
        params={
            "res": str(resource.id),
            "parent": str(location.parent_id),
        },
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2

    # wrong resource ID
    resp = await test_client.get(
        "/browse/context",
        params={"res": wrong_id},
    )
    assert_status(404, resp)

    # context of resource version
    await login()
    resp = await test_client.post(
        f"/resources/{str(resource.id)}/version",
    )
    assert_status(201, resp)
    assert "id" in resp.json()
    version_id = resp.json()["id"]
    resp = await test_client.get(
        "/browse/context",
        params={
            "res": version_id,
            "parent": str(location.parent_id),
        },
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2


@pytest.mark.anyio
async def test_get_location_data(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    wrong_id,
):
    text_id = (await insert_test_data())["texts"][0]
    assert len(text_id) > 0

    # get level 0 path and contents
    resp = await test_client.get(
        "/browse",
        params={"txt": text_id, "lvl": 0, "pos": 0},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["locationPath"]) > 0
    assert len(resp.json()["contents"]) == 2  # because enable_content_context=True

    # higher level
    resp = await test_client.get(
        "/browse",
        params={"txt": text_id, "lvl": 1, "pos": 0},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["locationPath"]) > 0
    assert len(resp.json()["contents"]) > 2

    # fail w/ invalid text ID
    resp = await test_client.get(
        "/browse",
        params={"txt": wrong_id, "lvl": 1, "pos": 0},
    )
    assert_status(404, resp)

    # fail w/ invalid location ID
    resp = await test_client.get(
        "/browse",
        params={"txt": text_id, "id": wrong_id},
    )
    assert_status(404, resp)


@pytest.mark.anyio
async def test_get_nearest_content_position(
    test_client: AsyncClient,
    assert_status,
    wrong_id,
    login,
    use_indices,
):
    resource = await ResourceBaseDocument.get(
        "67c043c0906e79b9062e22f4",
        with_children=True,
    )
    location = (
        await LocationDocument.find(
            LocationDocument.level == resource.level,
            LocationDocument.text_id == resource.text_id,
        )
        .sort(+LocationDocument.position)
        .first_or_none()
    )
    res_id = str(resource.id)
    loc_id = str(location.id)
    await login()

    # get nearest content position
    resp = await test_client.get(
        "/browse/nearest-content-location",
        params={
            "res": res_id,
            "loc": loc_id,
            "dir": "after",
        },
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)

    # fail to get nearest preceding content location
    resp = await test_client.get(
        "/browse/nearest-content-location",
        params={
            "res": res_id,
            "loc": loc_id,
            "dir": "before",
        },
    )
    assert_status(404, resp)

    # fail to get nearest content location with wrong resource ID
    resp = await test_client.get(
        "/browse/nearest-content-location",
        params={
            "res": wrong_id,
            "loc": loc_id,
            "dir": "after",
        },
    )
    assert_status(404, resp)

    # fail to get nearest content location with wrong location ID
    resp = await test_client.get(
        "/browse/nearest-content-location",
        params={
            "res": res_id,
            "loc": wrong_id,
            "dir": "after",
        },
    )
    assert_status(404, resp)

    # fail to get nearest content location with location
    # from different level then resource
    location_wrong_level = await LocationDocument.find_one(
        LocationDocument.level != resource.level,
        LocationDocument.text_id == resource.text_id,
    )
    resp = await test_client.get(
        "/browse/nearest-content-location",
        params={
            "res": res_id,
            "loc": str(location_wrong_level.id),
            "dir": "after",
        },
    )
    assert_status(400, resp)

    # fail to get nearest content location with location
    # from different text then resource
    location_wrong_text = await LocationDocument.find_one(
        LocationDocument.text_id != resource.text_id,
    )
    resp = await test_client.get(
        "/browse/nearest-content-location",
        params={
            "res": res_id,
            "loc": str(location_wrong_text.id),
            "dir": "after",
        },
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_crud_bookmarks(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    wrong_id,
    login,
):
    await insert_test_data("texts", "locations", "resources")
    superuser = await login(is_superuser=True)
    location_id = "67c040a0906e79b9062e22e8"  # hand-picked because we need a level 1 bm

    # fail to create bookmark with wrong location ID
    resp = await test_client.post(
        "/browse/bookmarks",
        json={
            "locationId": wrong_id,
            "comment": "FOO",
        },
    )
    assert_status(404, resp)

    # create bookmark
    resp = await test_client.post(
        "/browse/bookmarks",
        json={
            "locationId": location_id,
            "comment": "FOO",
        },
    )
    assert_status(201, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["comment"] == "FOO"
    assert "id" in resp.json()
    assert resp.json()["userId"] == superuser["id"]
    bookmark_id = resp.json()["id"]

    # create conflicting bookmark
    resp = await test_client.post(
        "/browse/bookmarks",
        json={
            "locationId": location_id,
            "comment": "This should not work",
        },
    )
    assert_status(409, resp)

    # get all user bookmarks
    resp = await test_client.get(
        "/browse/bookmarks",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert resp.json()[0]["comment"] == "FOO"

    # fail to delete with wrong ID
    resp = await test_client.delete(f"/browse/bookmarks/{wrong_id}")
    assert_status(404, resp)

    # fail to delete as wrong user
    await login()
    resp = await test_client.delete(f"/browse/bookmarks/{bookmark_id}")
    assert_status(403, resp)
    await login(user=superuser)

    # delete bookmark
    resp = await test_client.delete(f"/browse/bookmarks/{bookmark_id}")
    assert_status(204, resp)
