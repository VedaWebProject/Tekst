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
    text = await TextDocument.find_one(TextDocument.slug == "pond")
    assert text
    resource = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.text_id == text.id, with_children=True
    )
    assert resource

    resp = await test_client.get(
        "/browse/context",
        params={"res": str(resource.id)},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3

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
        params={"res": version_id},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3


@pytest.mark.anyio
async def test_get_location_data(
    test_client: AsyncClient,
    insert_test_data,
    get_test_data,
    assert_status,
    wrong_id,
):
    await insert_test_data("texts", "locations", "resources", "contents")
    texts = get_test_data("collections/texts.json", for_http=True)
    text_id = next((txt for txt in texts if txt["slug"] == "fdhdgg"), {}).get("_id", "")
    assert len(text_id) > 0

    # get level 0 path and contents
    resp = await test_client.get(
        "/browse",
        params={"txt": text_id, "lvl": 0, "pos": 0},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["locationPath"]) > 0
    assert len(resp.json()["contents"]) > 0

    # higher level
    resp = await test_client.get(
        "/browse",
        params={"txt": text_id, "lvl": 2, "pos": 0},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["locationPath"]) > 0
    assert len(resp.json()["contents"]) > 0

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
    insert_test_data,
    assert_status,
    wrong_id,
    login,
):
    await insert_test_data()
    resource = await ResourceBaseDocument.get(
        "654b825533ee5737b297f8f3",
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
