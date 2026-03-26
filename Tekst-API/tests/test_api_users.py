import pytest

from beanie import PydanticObjectId
from beanie.operators import Set
from fastapi.exceptions import HTTPException
from httpx import AsyncClient
from tekst.auth import create_initial_superuser
from tekst.models.resource import ResourceBaseDocument


@pytest.mark.anyio
async def test_admin_get_all_users(
    test_client: AsyncClient,
    insert_test_data,
    login,
    assert_status,
):
    await insert_test_data("users")
    await login(is_superuser=True)
    resp = await test_client.get("/users")
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 3


@pytest.mark.anyio
async def test_find_public_users(
    test_client: AsyncClient,
    login,
    assert_status,
):
    u = await login()

    # legitimate search
    resp = await test_client.get(
        "/users/public",
        params={"q": u.get("username")},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 1
    assert resp.json()["users"][0]["username"] == u["username"]
    assert "id" in resp.json()["users"][0]
    assert "name" in resp.json()["users"][0]
    assert "isVerified" not in resp.json()["users"][0]

    # nonsense search
    resp = await test_client.get(
        "/users/public",
        params={"q": "nonsense"},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0

    # no query, empty query = no results
    resp = await test_client.get(
        "/users/public",
        params={"emptyOk": False},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0

    # no query, empty query = all users
    resp = await test_client.get(
        "/users/public",
        params={"emptyOk": True},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) > 0

    # query of whitespaces
    resp = await test_client.get(
        "/users/public",
        params={"q": "      ", "emptyOk": False},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0


@pytest.mark.anyio
async def test_get_public_user(
    test_client: AsyncClient,
    register_test_user,
    assert_status,
):
    u = await register_test_user()

    # get by ID
    resp = await test_client.get(f"/users/public/{u['id']}")
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "username" in resp.json()
    assert resp.json()["username"] == u["username"]
    assert "id" in resp.json()
    assert "name" in resp.json()
    assert "isVerified" not in resp.json()

    # get by username
    resp = await test_client.get(f"/users/public/{u['username']}")
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "username" in resp.json()
    assert resp.json()["username"] == u["username"]
    assert "id" in resp.json()
    assert "name" in resp.json()
    assert "isVerified" not in resp.json()

    # fail to get by non-existent username
    resp = await test_client.get("/users/public/i_do_not_exist")
    assert_status(404, resp)


@pytest.mark.anyio
async def test_user_updates_self(
    login,
    test_client: AsyncClient,
    assert_status,
):
    await login()
    # get user data from /users/me
    resp = await test_client.get(
        "/users/me",
    )
    assert_status(200, resp)
    assert "id" in resp.json()
    # update own first name
    user_id = resp.json()["id"]
    updates = {"name": "Bird Person"}
    resp = await test_client.patch(
        "/users/me",
        json=updates,
    )
    assert_status(200, resp)
    assert resp.json()["id"] == user_id
    assert resp.json()["name"] == "Bird Person"


@pytest.mark.anyio
async def test_user_deletes_self(
    login,
    test_client: AsyncClient,
    assert_status,
    insert_test_data,
):
    await insert_test_data()
    u = await login()  # log in as (and thus create) regular user
    su = await login(is_superuser=True)  # log in as (and thus create) superuser
    target_res_id = PydanticObjectId("67c043c0906e79b9062e22f4")

    # get resource count
    res_count_before = await ResourceBaseDocument.find_all(with_children=True).count()

    # set superuser as owner of all resources
    await ResourceBaseDocument.find_all(with_children=True).update(
        Set({ResourceBaseDocument.owner_ids: [PydanticObjectId(su["id"])]})
    )
    assert (
        await ResourceBaseDocument.find(
            ResourceBaseDocument.owner_ids == PydanticObjectId(su["id"]),
            with_children=True,
        ).count()
        == res_count_before
    )

    # unpublish target resource
    await ResourceBaseDocument.find_one(
        ResourceBaseDocument.id == target_res_id,
        with_children=True,
    ).update(Set({ResourceBaseDocument.public: False}))
    assert (
        await ResourceBaseDocument.get(
            target_res_id,
            with_children=True,
        )
    ).public is False

    # check that patch for target resource exists and is owned by superuser su
    target_resource_patch = await ResourceBaseDocument.find_one(
        ResourceBaseDocument.original_id == target_res_id,
        with_children=True,
    )
    assert target_resource_patch
    assert target_resource_patch.owner_ids[0] == PydanticObjectId(su["id"])

    # set regular user as owner of target resource
    await ResourceBaseDocument.find(
        ResourceBaseDocument.id == target_res_id,
        with_children=True,
    ).update(Set({ResourceBaseDocument.owner_ids: [PydanticObjectId(u["id"])]}))
    target_resource: ResourceBaseDocument = await ResourceBaseDocument.get(
        target_res_id,
        with_children=True,
    )
    assert len(target_resource.owner_ids) == 1
    assert target_resource.owner_ids[0] == PydanticObjectId(u["id"])

    # delete self (as regular user)
    await login(user=u)
    resp = await test_client.delete("/users/me")
    assert_status(204, resp)

    # target resource formerly owned by deleted user should be deleted now, too
    assert not await ResourceBaseDocument.get(
        target_res_id,
        with_children=True,
    )

    # former patch of target resource should be a full-fledged resource now
    # (and is owned by superuser su)
    former_target_resource_patch = await ResourceBaseDocument.get(
        target_resource_patch.id,
        with_children=True,
    )
    assert former_target_resource_patch  # exists
    assert former_target_resource_patch.original_id is None  # not a patch anymore
    assert former_target_resource_patch.owner_ids[0] == PydanticObjectId(
        su["id"]
    )  # owner = su

    # delete self (as superuser)
    await login(user=su)
    resp = await test_client.delete(
        "/users/me",
    )
    assert_status(204, resp)

    # former patch of target resource should be deleted now, too
    assert (
        await ResourceBaseDocument.get(
            target_resource_patch.id,
            with_children=True,
        )
        is None
    )

    # check resource count (should be 2 less that at the beginning of test case)
    assert (
        await ResourceBaseDocument.find_all(
            with_children=True,
        ).count()
        == res_count_before - 2
    )


@pytest.mark.anyio
async def test_last_superuser_deletes_self_fails(
    login,
    test_client: AsyncClient,
    assert_status,
):
    await login(is_superuser=True)
    resp = await test_client.delete("/users/me")
    assert_status(403, resp)


@pytest.mark.anyio
async def test_update_user(
    login,
    register_test_user,
    test_client: AsyncClient,
    assert_status,
):
    user = await register_test_user(is_active=False)
    await login(is_superuser=True)
    # update user
    resp = await test_client.patch(
        f"/users/{user['id']}",
        json={"isActive": True, "isSuperuser": True, "password": "XoiPOI09871"},
    )
    assert_status(200, resp)
    assert resp.json()["isActive"] is True
    assert resp.json()["isSuperuser"] is True
    assert "password" not in resp.json()
    # update user again
    resp = await test_client.patch(
        f"/users/{user['id']}", json={"isActive": False, "isSuperuser": False}
    )
    assert_status(200, resp)
    assert resp.json()["isActive"] is False
    assert resp.json()["isSuperuser"] is False


@pytest.mark.anyio
async def test_create_initial_superuser(
    config,
    clear_db,
):
    await create_initial_superuser()  # will abort because of dev mode
    prod_cfg = config.model_copy(deep=True)
    prod_cfg.dev_mode = False
    await create_initial_superuser(prod_cfg)  # will create initial superuser


@pytest.mark.anyio
async def test_create_duplicate_user(
    login,
):
    with pytest.raises(HTTPException) as e:
        await login()
        await login()
        assert "REGISTER_USERNAME_ALREADY_EXISTS" in e.getrepr()
