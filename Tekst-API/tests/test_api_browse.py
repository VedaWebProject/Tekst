import pytest

from httpx import AsyncClient
from tekst.models.location import LocationDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.text import TextDocument


@pytest.mark.anyio
async def test_get_content_siblings(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wrong_id,
    login,
):
    await insert_sample_data("texts", "locations", "resources", "contents")
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
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3

    # wrong resource ID
    resp = await test_client.get(
        "/browse/content-siblings",
        params={"res": wrong_id},
    )
    assert status_assertion(404, resp)

    # siblings of resource version
    await login()
    resp = await test_client.post(
        f"/resources/{str(resource.id)}/version",
    )
    assert status_assertion(201, resp)
    assert "id" in resp.json()
    version_id = resp.json()["id"]
    resp = await test_client.get(
        "/browse/content-siblings",
        params={"res": version_id},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 3


@pytest.mark.anyio
async def test_get_location_data(
    test_client: AsyncClient,
    insert_sample_data,
    get_sample_data,
    status_assertion,
    wrong_id,
):
    await insert_sample_data("texts", "locations", "resources", "contents")
    texts = get_sample_data("db/texts.json", for_http=True)
    text_id = next((txt for txt in texts if txt["slug"] == "fdhdgg"), {}).get("_id", "")
    assert len(text_id) > 0

    # get level 0 path and contents
    resp = await test_client.get(
        "/browse/location-data",
        params={"txt": text_id, "lvl": 0, "pos": 0},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["locationPath"]) > 0
    assert len(resp.json()["contents"]) > 0

    # higher level
    resp = await test_client.get(
        "/browse/location-data",
        params={"txt": text_id, "lvl": 2, "pos": 0},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["locationPath"]) > 0
    assert len(resp.json()["contents"]) > 0

    # invalid location data
    resp = await test_client.get(
        "/browse/location-data",
        params={"txt": wrong_id, "lvl": 1, "pos": 0},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["locationPath"]) == 0
    assert len(resp.json()["contents"]) == 0


@pytest.mark.anyio
async def test_get_path_options_by_head(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wrong_id,
):
    await insert_sample_data("texts", "locations")
    text = await TextDocument.find_one(TextDocument.slug == "fdhdgg")
    location = await LocationDocument.find_one(
        LocationDocument.text_id == text.id, LocationDocument.level == 1
    )
    resp = await test_client.get(
        f"/browse/locations/{str(location.id)}/path/options-by-head",
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert isinstance(resp.json()[0], list)

    # invalid location data
    resp = await test_client.get(
        f"/browse/locations/{wrong_id}/path/options-by-head",
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_path_options_by_root(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wrong_id,
):
    await insert_sample_data("texts", "locations")
    text = await TextDocument.find_one(TextDocument.slug == "fdhdgg")
    location = await LocationDocument.find_one(
        LocationDocument.text_id == text.id, LocationDocument.level == 0
    )
    resp = await test_client.get(
        f"/browse/locations/{str(location.id)}/path/options-by-root",
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert isinstance(resp.json()[0], list)

    # invalid location data
    resp = await test_client.get(
        f"/browse/locations/{wrong_id}/path/options-by-root",
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_resource_coverage_data(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wrong_id,
):
    inserted_ids = await insert_sample_data(
        "texts", "locations", "resources", "contents"
    )
    resource_id = inserted_ids["resources"][0]

    # get coverage data
    resp = await test_client.get(
        f"/resources/{resource_id}/coverage",
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)

    # use invalid resource ID
    resp = await test_client.get(
        f"/resources/{wrong_id}/coverage",
    )
    assert status_assertion(404, resp)


@pytest.mark.anyio
async def test_get_nearest_content_position(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wrong_id,
    login,
):
    inserted_ids = await insert_sample_data(
        "texts", "locations", "resources", "contents"
    )
    resource_id = inserted_ids["resources"][0]
    await login()

    # get nearest content position
    resp = await test_client.get(
        "/browse/nearest-content-position",
        params={"res": resource_id, "pos": 0, "mode": "subsequent"},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), int)
    assert resp.json() == 1

    # fail to get nearest content position with wrong resource ID
    resp = await test_client.get(
        "/browse/nearest-content-position",
        params={"res": wrong_id, "pos": 0, "mode": "subsequent"},
    )
    assert status_assertion(404, resp)
