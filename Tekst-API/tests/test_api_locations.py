import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_location(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts"))["texts"][0]
    locations = [
        {"textId": text_id, "label": f"Location {n}", "level": 0, "position": n}
        for n in range(10)
    ]

    await login(is_superuser=True)

    for location in locations:
        resp = await test_client.post(
            "/locations",
            json=location,
        )
        assert resp.status_code == 201, status_fail_msg(201, resp)

    # invalid level
    resp = await test_client.post(
        "/locations",
        json={
            "textId": text_id,
            "label": "Invalid Location",
            "level": 4,
            "position": 0,
        },
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_create_additional_location(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    await login(is_superuser=True)

    # get a parent location
    resp = await test_client.get(
        "/locations", params={"txt": text_id, "lvl": 0, "pos": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1

    resp = await test_client.post(
        "/locations",
        json={
            "textId": text_id,
            "parentId": resp.json()[0]["id"],
            "label": "Additional Location",
            "level": 1,
            "position": 9999,
        },
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)


@pytest.mark.anyio
async def test_create_additional_location_only_child(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    await login(is_superuser=True)

    # create new location on level 0
    resp = await test_client.post(
        "/locations",
        json={
            "textId": text_id,
            "label": "Additional Location",
            "level": 0,
            "position": 9999,
        },
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert isinstance(resp.json(), dict)

    # create only-child location
    resp = await test_client.post(
        "/locations",
        json={
            "textId": text_id,
            "parentId": resp.json()["id"],
            "label": "Additional Location",
            "level": 1,
            "position": 9999,
        },
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)


@pytest.mark.anyio
async def test_child_location_io(
    test_client: AsyncClient,
    get_sample_data,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts"))["texts"][0]
    location = get_sample_data("db/locations.json", for_http=True)[0]
    await login(is_superuser=True)

    # create parent
    resp = await test_client.post(
        "/locations",
        json=location,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    parent = resp.json()
    assert parent["id"]

    # create child
    child = location
    child["parentId"] = parent["id"]
    child["level"] = parent["level"] + 1
    child["position"] = 0
    resp = await test_client.post(
        "/locations",
        json=child,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    child = resp.json()
    assert "id" in resp.json()
    assert "parentId" in resp.json()
    assert resp.json()["parentId"] == str(child["parentId"])

    # find children by parent ID
    resp = await test_client.get(
        "/locations", params={"txt": parent["textId"], "parent": parent["id"]}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(child["id"])

    # find children by parent ID using dedicated children endpoint
    resp = await test_client.get(
        "/locations/children",
        params={"parent": child["parentId"]},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(child["id"])

    # find children by text ID and null parent ID using dedicated children endpoint
    resp = await test_client.get(
        "/locations/children",
        params={"txt": text_id},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == str(parent["id"])

    # try to request children without parent or text ID
    resp = await test_client.get("/locations/children")
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_create_location_invalid_text_fail(
    test_client: AsyncClient,
    get_sample_data,
    insert_sample_data,
    status_fail_msg,
    login,
):
    await insert_sample_data("texts")
    location = get_sample_data("db/locations.json", for_http=True)[0]
    location["textId"] = "5ed7cfba5e32eb7759a17565"
    await login(is_superuser=True)

    resp = await test_client.post(
        "/locations",
        json=location,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_get_locations(
    test_client: AsyncClient,
    get_sample_data,
    insert_sample_data,
    status_fail_msg,
    wrong_id,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    locations = get_sample_data("db/locations.json", for_http=True)

    # test results length limit
    resp = await test_client.get(
        "/locations", params={"txt": text_id, "lvl": 0, "limit": 2}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2

    # test empty results with status 200
    resp = await test_client.get("/locations", params={"txt": wrong_id, "lvl": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # test results contain all locations of level 0
    resp = await test_client.get("/locations", params={"txt": text_id, "lvl": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == len(
        [n for n in locations if n["textId"] == text_id and n["level"] == 0]
    )

    # test returned locations have IDs
    assert "id" in resp.json()[0]
    # save location ID for later
    location_id = resp.json()[0]["id"]

    # test specific position
    resp = await test_client.get(
        "/locations", params={"txt": text_id, "lvl": 0, "pos": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1

    # test invalid request
    resp = await test_client.get("/locations", params={"txt": text_id})
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # test get specific location by ID
    resp = await test_client.get(f"/locations/{location_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == location_id

    # test get specific location by wrong ID
    resp = await test_client.get(f"/locations/{wrong_id}")
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_update_location(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]

    # get location from db
    resp = await test_client.get("/locations", params={"txt": text_id, "lvl": 0})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    location = resp.json()[0]

    # login
    await login(is_superuser=True)

    # update location
    location_update = {"label": "A fresh label"}
    resp = await test_client.patch(
        f"/locations/{location['id']}",
        json=location_update,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(location["id"])
    assert "label" in resp.json()
    assert resp.json()["label"] == "A fresh label"

    # update unchanged location
    resp = await test_client.patch(
        f"/locations/{location['id']}",
        json=location_update,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # update invalid location
    location_update = {"label": "Brand new label"}
    resp = await test_client.patch(
        "/locations/637b9ad396d541a505e5439b", json=location_update
    )
    assert resp.status_code == 400, status_fail_msg(
        400,
        resp,
    )


@pytest.mark.anyio
async def test_delete_location(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    wrong_id,
):
    text_id = (await insert_sample_data("texts", "locations", "resources"))["texts"][0]

    # get location from db
    resp = await test_client.get(
        "/locations", params={"txt": text_id, "lvl": 0, "pos": 0}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    location = resp.json()[0]

    # log in as superuser
    await login(is_superuser=True)

    # get existing resource
    resp = await test_client.get("/resources", params={"txt": text_id})
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    resource = resp.json()[0]

    # create plain text resource content
    payload = {
        "resourceId": resource["id"],
        "resourceType": "plainText",
        "locationId": location["id"],
        "text": "Ein Raabe geht im Feld spazieren.",
        "comment": "This is a comment",
    }
    resp = await test_client.post(
        "/contents",
        json=payload,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["text"] == payload["text"]
    assert resp.json()["comment"] == payload["comment"]
    assert "id" in resp.json()

    # delete location
    resp = await test_client.delete(
        f"/locations/{location['id']}",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json().get("locations", None) > 1
    assert resp.json().get("contents", None) == 1

    # delete location with wrong ID
    resp = await test_client.delete(
        f"/locations/{wrong_id}",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_move_location(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # get location from db
    resp = await test_client.get(
        "/locations",
        params={"txt": text_id, "lvl": 0, "pos": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    location = resp.json()[0]

    # move location
    resp = await test_client.post(
        f"/locations/{location['id']}/move",
        json={"position": 1, "after": True, "parentId": None},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["position"] == 1

    # move location with wrong parent ID
    resp = await test_client.post(
        f"/locations/{location['id']}/move",
        json={"position": 2, "after": True, "parentId": "637b9ad396d541a505e5439b"},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["position"] == 2


@pytest.mark.anyio
async def test_move_location_wrong_id(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
    wrong_id,
):
    # log in as superuser
    await login(is_superuser=True)

    # move location with wrong ID
    resp = await test_client.post(
        f"/locations/{wrong_id}/move",
        json={"position": 1, "after": True, "parentId": None},
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_move_location_lowest_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # get location from db
    resp = await test_client.get(
        "/locations",
        params={"txt": text_id, "lvl": 1, "pos": 0},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    location = resp.json()[0]
    assert location["level"] == 1
    assert location["position"] == 0

    # move
    resp = await test_client.post(
        f"/locations/{location['id']}/move",
        json={"position": 1, "after": True, "parentId": location["parentId"]},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["label"] == "1"
    assert resp.json()["level"] == 1
    assert resp.json()["position"] == 1
