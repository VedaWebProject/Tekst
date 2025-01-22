import json

import pytest

from beanie import PydanticObjectId
from beanie.operators import Set
from httpx import AsyncClient
from tekst.models.platform import PlatformStateDocument
from tekst.models.resource import ResourceBaseDocument


@pytest.mark.anyio
async def test_create_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    user = await login()
    payload = {
        "title": [{"locale": "*", "translation": "A test resource"}],
        "description": [
            {
                "locale": "*",
                "translation": "This is     a string with \n some space    chars",
            }
        ],
        "textId": text_id,
        "level": 0,
        "resourceType": "plainText",
        "ownerId": user["id"],
    }

    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert_status(201, resp)
    assert "id" in resp.json()
    assert resp.json()["title"][0]["translation"] == "A test resource"
    assert (
        resp.json()["description"][0]["translation"]
        == "This is a string with some space chars"
    )
    assert resp.json()["ownerId"] == user.get("id")


@pytest.mark.anyio
async def test_create_resource_w_invalid_type(
    test_client: AsyncClient,
    insert_sample_data,
    login,
    assert_status,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    user = await login()
    payload = {
        "title": [{"locale": "*", "translation": "A test resource"}],
        "description": [
            {
                "locale": "*",
                "translation": "This is     a string with \n some space    chars",
            }
        ],
        "textId": text_id,
        "level": 0,
        "resourceType": "foo",
        "ownerId": user["id"],
    }

    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert_status(422, resp)


@pytest.mark.anyio
async def test_create_too_many_resources(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    user = await login()

    error = None
    for i in range(100):
        resp = await test_client.post(
            "/resources",
            json={
                "title": [{"locale": "*", "translation": f"A test resource {i}"}],
                "textId": text_id,
                "level": 0,
                "resourceType": "plainText",
                "ownerId": user["id"],
            },
        )
        if resp.status_code == 409:
            error = resp.json()
            break
    assert error is not None
    assert error["detail"]["key"] == "resourcesLimitReached"


@pytest.mark.anyio
async def test_create_resource_w_invalid_level(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    user = await login()
    resp = await test_client.post(
        "/resources",
        json={
            "title": [{"locale": "*", "translation": "A test resource"}],
            "description": [
                {
                    "locale": "*",
                    "translation": "This is     a string with \n some space    chars",
                }
            ],
            "textId": text_id,
            "level": 4,
            "resourceType": "plainText",
            "ownerId": user["id"],
        },
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_create_resource_w_wrong_text_id(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    wrong_id,
):
    await insert_sample_data("texts", "locations")
    await login()

    payload = {
        "title": [{"locale": "*", "translation": "A test resource"}],
        "textId": wrong_id,
        "level": 0,
        "resourceType": "plainText",
    }

    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_create_resource_with_forged_owner_id(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
):
    text_id = (await insert_sample_data("texts", "locations"))["texts"][0]
    await login()

    # create new resource with made up owner ID
    payload = {
        "title": [{"locale": "*", "translation": "Foo Bar Baz"}],
        "textId": text_id,
        "level": 0,
        "resourceType": "plainText",
        "ownerId": "643d3cdc21efd6c46ae1527e",
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert_status(201, resp)
    assert resp.json()["ownerId"] != payload["ownerId"]


@pytest.mark.anyio
async def test_create_resource_with_denied_type(
    test_client: AsyncClient,
    insert_sample_data,
    login,
    assert_status,
):
    text_id = (await insert_sample_data())["texts"][0]
    await PlatformStateDocument.find().update(
        Set({PlatformStateDocument.deny_resource_types: ["plainText"]})
    )
    u = await login()

    resp = await test_client.post(
        "/resources",
        json={
            "title": [{"locale": "*", "translation": "Foo Bar Baz"}],
            "textId": text_id,
            "level": 0,
            "resourceType": "plainText",
            "ownerId": u["id"],
        },
    )
    assert_status(403, resp)


@pytest.mark.anyio
async def test_create_resource_version(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    wrong_id,
):
    resource_id = (await insert_sample_data("texts", "locations", "resources"))[
        "resources"
    ][0]
    user = await login()

    # create new resource version (fail with wrong resource ID)
    resp = await test_client.post(
        f"/resources/{wrong_id}/version",
    )
    assert_status(404, resp)

    # create new resource version
    resp = await test_client.post(
        f"/resources/{resource_id}/version",
    )
    assert_status(201, resp)
    assert "id" in resp.json()
    assert "originalId" in resp.json()
    assert "ownerId" in resp.json()
    assert resp.json()["ownerId"] == user.get("id")

    # fail to create new resource version of another version
    resp = await test_client.post(
        f"/resources/{resp.json()['id']}/version",
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_create_too_many_resource_versions(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
):
    resource_id = (await insert_sample_data("texts", "locations", "resources"))[
        "resources"
    ][0]
    await login()

    error = None
    for i in range(100):
        resp = await test_client.post(
            f"/resources/{resource_id}/version",
        )
        if resp.status_code == 409:
            error = resp.json()
            break
    assert error is not None
    assert error["detail"]["key"] == "resourcesLimitReached"


@pytest.mark.anyio
async def test_update_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    register_test_user,
    wrong_id,
    logout,
):
    text_id = (await insert_sample_data("texts", "locations", "resources"))["texts"][0]
    superuser = await login(is_superuser=True)
    other_user = await register_test_user()

    # create new resource (because only owner can update(write))
    payload = {
        "title": [{"locale": "*", "translation": "Foo Bar Baz"}],
        "textId": text_id,
        "level": 0,
        "resourceType": "plainText",
        "public": True,
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert_status(201, resp)
    resource_data = resp.json()
    assert "id" in resource_data
    assert "ownerId" in resource_data
    assert resource_data["ownerId"] == superuser.get("id")
    assert resource_data.get("public") is False

    # update resource
    updates = {
        "title": [{"locale": "*", "translation": "This Title Changed"}],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(resource_data["id"])
    assert resp.json()["title"] == updates["title"]

    # update resource w/ wrong ID
    updates = {
        "title": [{"locale": "*", "translation": "This Title Changed"}],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{wrong_id}",
        json=updates,
    )
    assert_status(404, resp)

    # update resource's read shares
    updates = {"sharedRead": [other_user["id"]], "resourceType": "plainText"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["sharedRead"][0] == other_user["id"]

    # update resource's read/write shares
    updates = {
        "sharedRead": [],
        "sharedWrite": [other_user["id"]],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["sharedRead"]) == 0
    assert resp.json()["sharedWrite"][0] == other_user["id"]

    # update resource's write shares using wrong user ID
    updates = {"sharedWrite": [wrong_id], "resourceType": "plainText"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(400, resp)

    # check if updating public/proposed has no effect (as intended)
    updates = {"public": True, "proposed": True, "resourceType": "plainText"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["public"] is False
    assert resp.json()["proposed"] is False

    # update resource unauthenticated
    await logout()
    updates = {"title": "This Title Changed Again", "resourceType": "plainText"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(401, resp)

    # update resource shares as non-owner/non-admin
    await login(user=other_user)
    updates = {"sharedRead": [wrong_id], "resourceType": "plainText"}
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert wrong_id not in resp.json()["sharedRead"]  # bc API should ignore the update!


@pytest.mark.anyio
async def test_set_shares_for_public_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    register_test_user,
    wrong_id,
):
    resource_id = (await insert_sample_data("texts", "locations", "resources"))[
        "resources"
    ][0]
    await login(is_superuser=True)
    other_user = await register_test_user()

    # set resource public
    res = await ResourceBaseDocument.get(resource_id, with_children=True)
    await res.set({ResourceBaseDocument.public: True})

    # update shares
    updates = {"sharedRead": [other_user["id"]], "resourceType": "plainText"}
    resp = await test_client.patch(
        f"/resources/{resource_id}",
        json=updates,
    )
    assert_status(200, resp)
    assert resp.json()["public"] is True
    assert len(resp.json()["sharedRead"]) == 0  # bc API should clear shares updates!


@pytest.mark.anyio
async def test_get_resource(
    test_client: AsyncClient,
    insert_sample_data,
    wrong_id,
    login,
    assert_status,
):
    resource_id = (await insert_sample_data("texts", "locations", "resources"))[
        "resources"
    ][0]

    # get resource by ID
    resp = await test_client.get(f"/resources/{resource_id}")
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    assert resp.json()["id"] == resource_id

    # fail to get resource by wrong ID
    resp = await test_client.get(f"/resources/{wrong_id}")
    assert_status(404, resp)

    # fail to get resource without read permissions
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == PydanticObjectId(resource_id),
        with_children=True,
    ).set({ResourceBaseDocument.public: False})
    await login(is_superuser=False)
    resp = await test_client.get(f"/resources/{resource_id}")
    assert_status(404, resp)


@pytest.mark.anyio
async def test_access_private_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    logout,
):
    inserted_ids = await insert_sample_data("texts", "locations", "resources")
    text_id = inserted_ids["texts"][0]
    resource_id = inserted_ids["resources"][0]

    # get all accessible resources
    resp = await test_client.get("/resources", params={"txt": text_id})
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    accessible_unauthorized = len(resp.json())

    # register test superuser
    await login(is_superuser=True)

    # unpublish
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert_status(200, resp)

    # get all accessible resources again, unauthenticated
    await logout()
    resp = await test_client.get("/resources", params={"txt": text_id})
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) < accessible_unauthorized  # this should be less now


@pytest.mark.anyio
async def test_get_resources(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
):
    text_id = (await insert_sample_data("texts", "locations", "resources"))["texts"][0]
    resp = await test_client.get(
        "/resources",
        params={"txt": text_id, "lvl": 2, "type": "plainText"},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    assert isinstance(resp.json()[0], dict)
    assert "id" in resp.json()[0]

    resource_id = resp.json()[0]["id"]

    resp = await test_client.get(f"/resources/{resource_id}")
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "resourceType" in resp.json()

    # request invalid ID
    resp = await test_client.get("/resources/foo")
    assert_status(422, resp)


@pytest.mark.anyio
async def test_propose_unpropose_publish_unpublish_resource(
    test_client: AsyncClient,
    insert_sample_data,
    login,
    wrong_id,
    assert_status,
):
    text_id = (await insert_sample_data("texts", "locations", "resources"))["texts"][0]
    owner = await login(is_superuser=True)

    # create new resource (because only owner can update(write))
    payload = {
        "title": [{"locale": "*", "translation": "Foo Bar Baz"}],
        "textId": text_id,
        "level": 0,
        "resourceType": "plainText",
        "ownerId": owner.get("id"),
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert_status(201, resp)
    resource_data = resp.json()
    assert "id" in resource_data
    assert "ownerId" in resource_data
    resource_id = resource_data["id"]

    # publish unproposed resource
    resp = await test_client.post(
        f"/resources/{resource_id}/publish",
    )
    assert_status(400, resp)

    # propose resource
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert_status(200, resp)

    # propose resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/propose",
    )
    assert_status(404, resp)

    # fail to propose resource version
    # create new resource version
    resp = await test_client.post(
        f"/resources/{resource_id}/version",
    )
    assert_status(201, resp)
    assert "id" in resp.json()
    version_id = resp.json()["id"]
    resp = await test_client.post(
        f"/resources/{version_id}/propose",
    )
    assert_status(400, resp)

    # get all accessible resources, check if ours is proposed
    resp = await test_client.get("/resources", params={"txt": text_id})
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    for resource in resp.json():
        if resource["id"] == resource_id:
            assert resource["proposed"]

    # propose resource again (should just go through)
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert_status(200, resp)

    # publish resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/publish",
    )
    assert_status(404, resp)

    # fail to publish resource version
    # (this should be actually be impossible anyway,
    # because we can't even propose a version... so we create
    # an invalid resource state on purpose, here)
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == PydanticObjectId(version_id),
        with_children=True,
    ).set({ResourceBaseDocument.proposed: True})
    resp = await test_client.post(
        f"/resources/{version_id}/publish",
    )
    assert_status(400, resp)

    # publish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/publish",
    )
    assert_status(200, resp)
    assert resp.json()["id"] == resource_id

    # publish already public resource again (should just go through)
    resp = await test_client.post(
        f"/resources/{resource_id}/publish",
    )
    assert_status(200, resp)
    assert resp.json()["id"] == resource_id

    # propose public resource
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert_status(400, resp)

    # unpublish resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/unpublish",
    )
    assert_status(404, resp)

    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert_status(200, resp)

    # unpublish resource again (should just go through)
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert_status(200, resp)

    # propose resource again
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert_status(200, resp)

    # unpropose resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/unpropose",
    )
    assert_status(404, resp)

    # unpropose resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpropose",
    )
    assert_status(200, resp)

    # propose resource unauthorized
    other_user = await login()
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert_status(403, resp)

    # propose resource again
    await login(user=owner)
    resp = await test_client.post(
        f"/resources/{resource_id}/propose",
    )
    assert_status(200, resp)

    # unpropose resource unauthorized
    await login(user=other_user)
    resp = await test_client.post(
        f"/resources/{resource_id}/unpropose",
    )
    assert_status(403, resp)


@pytest.mark.anyio
async def test_delete_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    wrong_id,
):
    inserted_ids = await insert_sample_data("texts", "locations", "resources")
    text_id = inserted_ids["texts"][0]
    resource_id = inserted_ids["resources"][0]

    # get all accessible resources
    resp = await test_client.get("/resources", params={"txt": text_id})
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    resources_count = len(resp.json())

    # register test users
    user = await login(is_superuser=True)

    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )

    # try to delete resource w/ wrong ID
    resp = await test_client.delete(
        f"/resources/{wrong_id}",
    )
    assert_status(404, resp)

    # become non-owner/non-superuser
    await login()

    # try to delete resource as non-owner/non-superuser
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert_status(403, resp)

    # become superuser again
    await login(user=user)

    # delete resource
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert_status(204, resp)

    # get all accessible resources again
    resp = await test_client.get("/resources", params={"txt": text_id})
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == resources_count - 1


@pytest.mark.anyio
async def test_delete_public_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
):
    inserted_ids = await insert_sample_data("texts", "locations", "resources")
    resource_id = inserted_ids["resources"][0]
    await login(is_superuser=True)

    # ensure resource is public
    resp = await test_client.post(f"/resources/{resource_id}/unpublish")
    resp = await test_client.post(f"/resources/{resource_id}/propose")
    assert_status(200, resp)
    assert resp.json()["proposed"] is True
    resp = await test_client.post(f"/resources/{resource_id}/publish")
    assert_status(200, resp)
    assert resp.json()["public"] is True

    # delete public resource (should not be possible)
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_delete_proposed_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
):
    inserted_ids = await insert_sample_data("texts", "locations", "resources")
    resource_id = inserted_ids["resources"][0]
    await login(is_superuser=True)

    # ensure resource is not public
    resp = await test_client.post(f"/resources/{resource_id}/unpublish")
    assert_status(200, resp)
    assert resp.json()["public"] is False

    # ensure resource is proposed
    resp = await test_client.post(f"/resources/{resource_id}/propose")
    assert_status(200, resp)
    assert resp.json()["proposed"] is True

    # delete proposed resource (should not be possible)
    resp = await test_client.delete(
        f"/resources/{resource_id}",
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_transfer_resource(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    register_test_user,
    wrong_id,
):
    inserted_ids = await insert_sample_data("texts", "locations", "resources")
    resource_id = inserted_ids["resources"][0]

    # register regular test user
    user = await register_test_user(is_superuser=False)
    # register test superuser
    superuser = await login(is_superuser=True)

    # transfer resource that is still public to test user
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert_status(400, resp)

    # unpublish resource
    resp = await test_client.post(
        f"/resources/{resource_id}/unpublish",
    )
    assert_status(200, resp)

    # transfer resource w/ wrong ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/transfer",
        json=user["id"],
    )
    assert_status(404, resp)

    # transfer resource to user w/ wrong ID
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=wrong_id,
    )
    assert_status(400, resp)

    # transfer resource without permission
    await login(user=user)
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert_status(403, resp)

    # transfer resource to test user
    await login(user=superuser)
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["ownerId"] == user["id"]

    # ....and do that again
    resp = await test_client.post(
        f"/resources/{resource_id}/transfer",
        json=user["id"],
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["ownerId"] == user["id"]


@pytest.mark.anyio
async def test_get_resource_template(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    wrong_id,
):
    inserted_ids = await insert_sample_data("texts", "locations", "resources")
    resource_id = inserted_ids["resources"][0]

    # try to get resource template (only for users with write permission)
    await login(is_superuser=False)
    resp = await test_client.get(
        f"/resources/{resource_id}/template",
    )
    assert_status(403, resp)

    # get resource template
    await login(is_superuser=True)
    resp = await test_client.get(
        f"/resources/{resource_id}/template",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)

    # get resource template w/ wrong ID
    resp = await test_client.get(
        f"/resources/{wrong_id}/template",
    )
    assert_status(404, resp)


@pytest.mark.anyio
async def test_import_resource_contents(
    test_client: AsyncClient,
    insert_sample_data,
    get_sample_data_path,
    assert_status,
    login,
    wrong_id,
    wait_for_task_success,
):
    inserted_ids = await insert_sample_data(
        "texts", "locations", "resources", "contents"
    )
    text_id = inserted_ids["texts"][1]
    superuser = await login(is_superuser=True)

    # create an additional location (so we can import new content for it and
    # don't only have updates to existing content)
    resp = await test_client.post(
        "/locations",
        json={"textId": text_id, "label": "Location!!", "level": 0, "position": 3},
    )
    assert_status(201, resp)
    additional_location_id = resp.json()["id"]

    # define sample data
    resource_id = "654ba525ec7833e469dde77e"
    sample_data = {
        "contents": [
            {"locationId": "654ba282ec7833e469dde766", "text": "FOO"},
            {"locationId": "654ba288ec7833e469dde768", "text": "BAR"},
            {"locationId": additional_location_id, "text": "BAZ"},
        ],
        "resourceId": resource_id,
    }
    sample_data_string = json.dumps(sample_data)

    # upload invalid resource data file (invalid JSON)
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={"file": ("foo.json", r"{foo: bar}", "application/json")},
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to upload with wrong mime type
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={"file": ("foo.json", sample_data_string, "text/plain")},
    )
    assert_status(400, resp)

    # fail to upload resource data file for wrong resource ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/import",
        files={"file": ("foo.json", sample_data_string, "application/json")},
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to upload w/ invalid location ID
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": (
                "foo.json",
                json.dumps(
                    {
                        "contents": [
                            {"locationId": "654ba282ec7833e469dde766", "text": "FOO"},
                            {"locationId": wrong_id, "text": "BAR"},
                            {"locationId": additional_location_id, "text": "BAZ"},
                        ],
                        "resourceId": resource_id,
                    }
                ),
                "application/json",
            )
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to upload w/ invalid content object
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": (
                "foo.json",
                json.dumps(
                    {
                        "contents": [
                            {"locationId": "654ba282ec7833e469dde766", "text": 1},
                            {"locationId": "654ba288ec7833e469dde768", "text": True},
                            {
                                "locationId": additional_location_id,
                                "text": ["foo", "bar"],
                            },
                        ],
                        "resourceId": resource_id,
                    }
                ),
                "application/json",
            )
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to upload w/ invalid contents prop type
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": (
                "foo.json",
                json.dumps(
                    {
                        "contents": {"foo": "bar"},
                        "resourceId": resource_id,
                    }
                ),
                "application/json",
            )
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # upload valid resource data file
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={"file": ("foo.json", sample_data_string, "application/json")},
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # fail to upload resource data without write permissions
    await login()
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={"file": ("foo.json", sample_data_string, "application/json")},
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])
    await login(user=superuser)

    # upload incomplete content data (one content without location ID)
    invalid_sample_data = sample_data.copy()
    del invalid_sample_data["contents"][0]["locationId"]
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": ("foo.json", json.dumps(invalid_sample_data), "application/json")
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # upload invalid content data (text is list[int])
    invalid_sample_data = sample_data.copy()
    invalid_sample_data["contents"][0]["text"] = [1, 2, 3]
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": ("foo.json", json.dumps(invalid_sample_data), "application/json")
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])


@pytest.mark.anyio
async def test_export_content(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    logout,
    wait_for_task_success,
    wrong_id,
    config,
):
    await insert_sample_data()
    await login()

    formats = [
        "json",
        "csv",
        "tekst-json",
    ]
    targets = [
        {
            "res_id": "66471b68ba9e65342c8e495b",
            "from_loc_id": "654b825533ee5737b297f8e5",
            "to_loc_id": "654b825533ee5737b297f8f2",
        },
        {
            "res_id": "6656cc7b81a66322c1bffb24",
            "from_loc_id": "654b825533ee5737b297f8e5",
            "to_loc_id": "654b825533ee5737b297f8f2",
        },
        {
            "res_id": "6641ce24affa6cb96bc85a55",
            "from_loc_id": "664321104aa6341acd83fb05",
            "to_loc_id": "664321104aa6341acd83fb05",
        },
        {
            "res_id": "6641d510affa6cb96bc85a5b",
            "from_loc_id": "664321104aa6341acd83fb05",
            "to_loc_id": "664321104aa6341acd83fb05",
        },
        {
            "res_id": "6641d2bfaffa6cb96bc85a58",
            "from_loc_id": "664321104aa6341acd83fb05",
            "to_loc_id": "664321104aa6341acd83fb05",
        },
        {
            "res_id": "67472c393d0d7622956981c9",
            "from_loc_id": "664321104aa6341acd83fb05",
            "to_loc_id": "664321104aa6341acd83fb05",
        },
        {
            "res_id": "6791146a74030487c64fe55f",
            "from_loc_id": "664321104aa6341acd83fb05",
            "to_loc_id": "664321104aa6341acd83fb05",
        },
    ]

    for fmt in formats:
        for target in targets:
            # create export
            resp = await test_client.get(
                f"/resources/{target['res_id']}/export",
                params={
                    "format": fmt,
                    "from": target["from_loc_id"],
                    "to": target["to_loc_id"],
                },
            )
            assert_status(202, resp)
            assert "id" in resp.json()
            assert await wait_for_task_success(resp.json()["id"])
            # download generated artifact
            resp = await test_client.get(
                "/platform/tasks/download",
                params={"pickupKey": resp.json()["pickupKey"]},
            )
            assert_status(200, resp)

    # log out for the next tests
    await logout()

    # fail to export w/ wrong resource ID
    resp = await test_client.get(
        f"/resources/{wrong_id}/export",
        params={
            "format": "csv",
            "from": "654b825533ee5737b297f8e5",
            "to": "654b825533ee5737b297f8f2",
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to export tekst-json as non-user
    resp = await test_client.get(
        "/resources/66471b68ba9e65342c8e495b/export",
        params={
            "format": "tekst-json",
            "from": "654b825533ee5737b297f8e5",
            "to": "654b825533ee5737b297f8f2",
        },
    )
    assert_status(403, resp)

    # fail to export w/ invalid location range
    resp = await test_client.get(
        "/resources/66471b68ba9e65342c8e495b/export",
        params={
            "format": "csv",
            "from": "654b825533ee5737b297f8e5",  # this location is on level 2
            "to": "654b825533ee5737b297f8e4",  # this location is on level 1
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to export without read permissions...
    # set public = False on resource
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == PydanticObjectId("66471b68ba9e65342c8e495b"),
        with_children=True,
    ).update(Set({ResourceBaseDocument.public: False}))
    # request export
    resp = await test_client.get(
        "/resources/66471b68ba9e65342c8e495b/export",
        params={
            "format": "csv",
            "from": "654b825533ee5737b297f8e5",
            "to": "654b825533ee5737b297f8f2",
        },
    )
    assert_status(202, resp)
    assert not await wait_for_task_success(resp.json()["id"])


@pytest.mark.anyio
async def test_trigger_maintenance(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    wait_for_task_success,
):
    await insert_sample_data("texts", "locations", "resources")
    await login(is_superuser=True)

    resp = await test_client.get("/resources/maintenance")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])


@pytest.mark.anyio
async def test_get_aggregations(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    wait_for_task_success,
    wrong_id,
):
    await insert_sample_data()
    await login(is_superuser=True)

    # fail to get aggregations (none yet, expect empty array)
    res_id = "6656cc7b81a66322c1bffb24"
    resp = await test_client.get(f"/resources/{res_id}/aggregations")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # run resource maintenance to generate aggregations
    resp = await test_client.get("/resources/maintenance")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get aggregations
    res_id = "6656cc7b81a66322c1bffb24"
    resp = await test_client.get(f"/resources/{res_id}/aggregations")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 1

    # fail to get aggregations for wrong resource ID
    resp = await test_client.get(f"/resources/{wrong_id}/aggregations")
    assert_status(404, resp)

    # fail to get aggregations for non-annotation resource
    res_id = "66471de0ba9e65342c8e4995"
    resp = await test_client.get(f"/resources/{res_id}/aggregations")
    assert_status(400, resp)


@pytest.mark.anyio
async def test_get_resource_coverage_data(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    wrong_id,
    login,
    wait_for_task_success,
):
    inserted_ids = await insert_sample_data()
    resource_id = inserted_ids["resources"][0]

    # get coverage data (none yet)
    resp = await test_client.get(
        f"/resources/{resource_id}/coverage",
    )
    assert_status(404, resp)

    # run resource maintenance to generate coverage data
    await login(is_superuser=True)
    resp = await test_client.get("/resources/maintenance")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get coverage data
    resp = await test_client.get(
        f"/resources/{resource_id}/coverage",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["ranges"]) > 0

    # fail w/ invalid resource ID
    resp = await test_client.get(
        f"/resources/{wrong_id}/coverage",
    )
    assert_status(404, resp)
