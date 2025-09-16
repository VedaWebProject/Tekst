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
    insert_test_data,
    assert_status,
    login,
):
    text_id = (await insert_test_data("texts", "locations"))["texts"][0]
    user = await login()
    payload = {
        "title": [{"locale": "*", "translation": "A test resource"}],
        "subtitle": [
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
        resp.json()["subtitle"][0]["translation"]
        == "This is a string with some space chars"
    )
    assert resp.json()["ownerId"] == user.get("id")


@pytest.mark.anyio
async def test_create_resource_w_invalid_type(
    test_client: AsyncClient,
    insert_test_data,
    login,
    assert_status,
):
    text_id = (await insert_test_data("texts", "locations"))["texts"][0]
    user = await login()
    payload = {
        "title": [{"locale": "*", "translation": "A test resource"}],
        "subtitle": [
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
    insert_test_data,
    assert_status,
    login,
):
    text_id = (await insert_test_data("texts", "locations"))["texts"][0]
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
    insert_test_data,
    assert_status,
    login,
):
    text_id = (await insert_test_data("texts", "locations"))["texts"][0]
    user = await login()
    resp = await test_client.post(
        "/resources",
        json={
            "title": [{"locale": "*", "translation": "A test resource"}],
            "subtitle": [
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
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    await insert_test_data("texts", "locations")
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
    insert_test_data,
    assert_status,
    login,
):
    text_id = (await insert_test_data("texts", "locations"))["texts"][0]
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
    insert_test_data,
    login,
    assert_status,
):
    text_id = (await insert_test_data())["texts"][0]
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
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    resource_id = (await insert_test_data("texts", "locations", "resources"))[
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
    insert_test_data,
    assert_status,
    login,
):
    resource_id = (await insert_test_data("texts", "locations", "resources"))[
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
    insert_test_data,
    assert_status,
    login,
    register_test_user,
    wrong_id,
    logout,
):
    text_id = (await insert_test_data("texts", "locations", "resources"))["texts"][0]
    superuser = await login(is_superuser=True)
    other_user = await register_test_user()

    # create new resource (because only owner can update(write))
    payload = {
        "title": [{"locale": "*", "translation": "Foo Bar Baz"}],
        "textId": text_id,
        "level": 0,
        "resourceType": "plainText",
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

    # update resource title
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

    # update resource config: search replacements
    updates = {
        "config": {
            "special": {"searchReplacements": [{"pattern": "a", "replacement": "o"}]}
        },
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["config"]["special"]["searchReplacements"][0]["pattern"] == "a"

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
    updates = {
        "sharedRead": [other_user["id"]],
        "resourceType": "plainText",
    }
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
    assert len(resp.json()["sharedWrite"]) == 1
    assert resp.json()["sharedWrite"][0] == other_user["id"]

    # update resource shares with write access but as non-owner/non-admin
    await login(user=other_user)
    updates = {
        "sharedRead": [superuser["id"]],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert superuser["id"] not in resp.json()["sharedRead"]

    # update resource's write shares using wrong user ID (should be filtered out)

    await login(user=superuser)
    updates = {
        "sharedWrite": [wrong_id],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert len(resp.json()["sharedWrite"]) == 0

    # check if updating public/proposed fields has no effect (as intended)
    await login(user=superuser)
    updates = {
        "public": True,
        "proposed": True,
        "resourceType": "plainText",
    }
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
    updates = {
        "title": [{"locale": "*", "translation": "This Title Changed"}],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(401, resp)

    # reset shares
    await login(user=superuser)
    updates = {
        "sharedRead": [],
        "sharedWrite": [],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["public"] is False
    assert resp.json()["proposed"] is False

    # update shares without write access
    await login(user=other_user)
    updates = {
        "title": [{"locale": "*", "translation": "This Title Changed"}],
        "resourceType": "plainText",
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(404, resp)


@pytest.mark.anyio
async def test_update_resource_searchability(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    register_test_user,
    wrong_id,
    logout,
    wait_for_task_success,
):
    text_id = (await insert_test_data("texts", "locations", "resources"))["texts"][0]
    superuser = await login(is_superuser=True)

    # create new resource (because only owner can update(write))
    payload = {
        "title": [{"locale": "*", "translation": "Foo Bar Baz"}],
        "textId": text_id,
        "level": 0,
        "resourceType": "plainText",
    }
    resp = await test_client.post(
        "/resources",
        json=payload,
    )
    assert_status(201, resp)
    resource_data = resp.json()
    assert "id" in resource_data
    assert resource_data["ownerId"] == superuser.get("id")
    assert resource_data["public"] is False
    assert resource_data["config"]["general"]["searchableQuick"] is True
    assert resource_data["config"]["general"]["searchableAdv"] is True

    # propose resource for publication
    # (because we need this step before publishing it)
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/propose",
    )
    assert_status(200, resp)

    # publish resource
    # (bacause what we're about to do only has an effect if the resource is public)
    resp = await test_client.post(
        f"/resources/{resource_data['id']}/publish",
    )
    assert_status(200, resp)

    # update/create search index
    resp = await test_client.get("/search/index/create")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # make sure text's `index_utd` is True
    resp = await test_client.get(
        f"/texts/{text_id}",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["indexUtd"] is True

    # update published resource's searchability
    updates = {
        "resourceType": "plainText",
        "config": {
            "general": {
                "searchableQuick": False,
                "searchableAdv": False,
            }
        },
    }
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["id"] == resource_data["id"]
    assert resp.json()["config"]["general"]["searchableQuick"] is False
    assert resp.json()["config"]["general"]["searchableAdv"] is False

    # make sure text's `index_utd` is False now
    resp = await test_client.get(
        f"/texts/{text_id}",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["indexUtd"] is False

    # update/create search index again
    resp = await test_client.get("/search/index/create")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # make sure text's `index_utd` is True now
    resp = await test_client.get(
        f"/texts/{text_id}",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["indexUtd"] is True

    # run same resource updates again to cover case of unmodified config
    resp = await test_client.patch(
        f"/resources/{resource_data['id']}",
        json=updates,
    )
    assert_status(200, resp)

    # make sure text's `index_utd` is still True
    resp = await test_client.get(
        f"/texts/{text_id}",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["indexUtd"] is True


@pytest.mark.anyio
async def test_set_shares_for_public_resource(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    register_test_user,
    wrong_id,
):
    resource_id = (
        await insert_test_data(
            "texts",
            "locations",
            "resources",
        )
    )["resources"][0]
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
    insert_test_data,
    wrong_id,
    login,
    assert_status,
):
    resource_id = (await insert_test_data("texts", "locations", "resources"))[
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
    insert_test_data,
    assert_status,
    login,
    logout,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources")
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
    insert_test_data,
    assert_status,
):
    text_id = (await insert_test_data("texts", "locations", "resources"))["texts"][0]
    resp = await test_client.get(
        "/resources",
        params={"txt": text_id, "lvl": 1, "type": "plainText"},
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
    insert_test_data,
    login,
    wrong_id,
    assert_status,
):
    text_id = (await insert_test_data("texts", "locations", "resources"))["texts"][0]
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
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources")
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
    insert_test_data,
    assert_status,
    login,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources")
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
    insert_test_data,
    assert_status,
    login,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources")
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
    insert_test_data,
    assert_status,
    login,
    register_test_user,
    wrong_id,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources")
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
    insert_test_data,
    assert_status,
    login,
    wrong_id,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources")
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
async def test_import_resource(
    test_client: AsyncClient,
    insert_test_data,
    get_test_data_path,
    assert_status,
    login,
    wrong_id,
    wait_for_task_success,
):
    inserted_ids = await insert_test_data("texts", "locations", "resources", "contents")
    text_id = inserted_ids["texts"][0]
    superuser = await login(is_superuser=True)

    # create an additional location (so we can import new content for it and
    # don't only have updates to existing content)
    resp = await test_client.post(
        "/locations",
        json={
            "textId": text_id,
            "label": "Three",
            "aliases": ["two-three", "2-3"],
            "level": 1,
            "position": 4,
            "parentId": "67c0406f906e79b9062e22e7",
        },
    )
    assert_status(201, resp)
    additional_location_id = resp.json()["id"]

    # define sample data
    resource_id = "67c043c0906e79b9062e22f4"
    import_sample = {
        "contents": [
            {
                "locationId": "67c040a0906e79b9062e22e8",
                "text": "FOO",
                "authors_comment": "foo\n\nbar\n\nbaz\n\nqux",
                "editors_comments": [
                    {"by": "Tekst", "comment": "quux\n\nquuux\n\nquuuxx\n\nquuuxxx"}
                ],
            },
            {"locationId": "67c040bb906e79b9062e22e9", "text": "BAR"},
            {"locationId": additional_location_id, "text": "QUUX"},
        ],
        "resourceId": resource_id,
    }
    import_sample_string = json.dumps(import_sample)

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
        files={"file": ("foo.json", import_sample_string, "text/plain")},
    )
    assert_status(400, resp)

    # fail to upload resource data file for wrong resource ID
    resp = await test_client.post(
        f"/resources/{wrong_id}/import",
        files={"file": ("foo.json", import_sample_string, "application/json")},
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
                            {"locationId": "67c040a0906e79b9062e22e8", "text": "FOO"},
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

    # fail to upload w/ invalid content field value
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": (
                "foo.json",
                json.dumps(
                    {
                        "contents": [
                            {"locationId": "67c040a0906e79b9062e22e8", "text": 1},
                            {"locationId": "67c040a0906e79b9062e22e9", "text": True},
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
        files={"file": ("foo.json", import_sample_string, "application/json")},
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # fail to upload resource data without write permissions
    await login()
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={"file": ("foo.json", import_sample_string, "application/json")},
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])
    await login(user=superuser)

    # upload incomplete content data (one content without location ID)
    invalid_import_sample = import_sample.copy()
    del invalid_import_sample["contents"][0]["locationId"]
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": ("foo.json", json.dumps(invalid_import_sample), "application/json")
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # upload invalid content data (text is list[int])
    invalid_import_sample = import_sample.copy()
    invalid_import_sample["contents"][0]["text"] = [1, 2, 3]
    resp = await test_client.post(
        f"/resources/{resource_id}/import",
        files={
            "file": ("foo.json", json.dumps(invalid_import_sample), "application/json")
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])


@pytest.mark.anyio
async def test_export_content(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    logout,
    wait_for_task_success,
    wrong_id,
    config,
):
    await insert_test_data()
    await login(is_superuser=True)

    formats = [
        "json",
        "csv",
        "tekst-json",
    ]
    target_res_ids = [
        "67c043c0906e79b9062e22f4",
        "67c04415906e79b9062e22f5",
        "67c0442e906e79b9062e22f6",
        "67c04445906e79b9062e22f7",
        "67c0444e906e79b9062e22f8",
        "67c0445b906e79b9062e22f9",
        "67c04473906e79b9062e22fa",
        "67c04473906e79b9062e22fb",
    ]

    from_loc_id = "67c040a0906e79b9062e22e8"
    to_loc_id = "67c042cf906e79b9062e22ed"

    for fmt in formats:
        for target_res_id in target_res_ids:
            # create export
            resp = await test_client.get(
                f"/resources/{target_res_id}/export",
                params={
                    "format": fmt,
                    "from": from_loc_id,
                    "to": to_loc_id,
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

            # if format is Tekst-JSON, make sure re-import works
            if fmt == "tekst-json":
                resp = await test_client.post(
                    f"/resources/{target_res_id}/import",
                    files={
                        "file": (
                            "foo.json",
                            json.dumps(resp.json()),
                            "application/json",
                        )
                    },
                )
                assert_status(202, resp)
                assert "id" in resp.json()
                assert await wait_for_task_success(resp.json()["id"])

    # log out for the next tests
    await logout()

    # fail to export w/ wrong resource ID
    resp = await test_client.get(
        f"/resources/{wrong_id}/export",
        params={
            "format": "csv",
            "from": from_loc_id,
            "to": to_loc_id,
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to export tekst-json as non-user
    resp = await test_client.get(
        f"/resources/{target_res_ids[0]}/export",
        params={
            "format": "tekst-json",
            "from": from_loc_id,
            "to": to_loc_id,
        },
    )
    assert_status(403, resp)

    # fail to export w/ invalid location range
    resp = await test_client.get(
        f"/resources/{target_res_ids[0]}/export",
        params={
            "format": "csv",
            "from": from_loc_id,  # this location is on level 1
            "to": "67c0406f906e79b9062e22e7",  # this location is on level 0
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert not await wait_for_task_success(resp.json()["id"])

    # fail to export without read permissions...
    # set public = False on resource
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == PydanticObjectId(target_res_ids[0]),
        with_children=True,
    ).update(Set({ResourceBaseDocument.public: False}))
    # request export
    resp = await test_client.get(
        f"/resources/{target_res_ids[0]}/export",
        params={
            "format": "csv",
            "from": from_loc_id,
            "to": to_loc_id,
        },
    )
    assert_status(202, resp)
    assert not await wait_for_task_success(resp.json()["id"])


@pytest.mark.anyio
async def test_trigger_resource_precomputation(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wait_for_task_success,
):
    await insert_test_data("texts", "locations", "resources")
    await login(is_superuser=True)

    resp = await test_client.get("/resources/precompute")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])


@pytest.mark.anyio
async def test_get_aggregations(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wait_for_task_success,
    wrong_id,
):
    await insert_test_data()
    await login(is_superuser=True)

    # fail to get aggregations (none yet, expect empty array)
    res_id = "67c0442e906e79b9062e22f6"
    resp = await test_client.get(f"/resources/{res_id}/aggregations")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # run resource precompute hooks to generate aggregations
    resp = await test_client.get("/resources/precompute")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get aggregations
    res_id = "67c0442e906e79b9062e22f6"
    resp = await test_client.get(f"/resources/{res_id}/aggregations")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 1

    # fail to get aggregations for wrong resource ID
    resp = await test_client.get(f"/resources/{wrong_id}/aggregations")
    assert_status(404, resp)


@pytest.mark.anyio
async def test_get_resource_coverage_data(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    wrong_id,
    login,
    wait_for_task_success,
):
    inserted_ids = await insert_test_data()
    resource_id = inserted_ids["resources"][0]

    # get coverage data (none yet)
    resp = await test_client.get(
        f"/resources/{resource_id}/coverage",
    )
    assert_status(404, resp)

    # run resource data precomputation to generate coverage data
    await login(is_superuser=True)
    resp = await test_client.get("/resources/precompute")
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
