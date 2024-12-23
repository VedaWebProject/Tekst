import pytest

from fastapi.exceptions import HTTPException
from httpx import AsyncClient
from tekst.auth import create_initial_superuser


@pytest.mark.anyio
async def test_admin_get_all_users(
    test_client: AsyncClient,
    insert_sample_data,
    login,
    assert_status,
):
    await insert_sample_data("users")
    await login(is_superuser=True)
    resp = await test_client.get("/users")
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 5


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
):
    await login()
    # delete self
    resp = await test_client.delete(
        "/users/me",
    )
    assert_status(204, resp)


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
async def test_create_initial_superuser():
    await create_initial_superuser()  # will abort because of dev mode
    await create_initial_superuser(force=True)  # forced despite dev mode


@pytest.mark.anyio
async def test_create_duplicate_user(login):
    with pytest.raises(HTTPException) as e:
        await login()
        await login()
        assert "REGISTER_USERNAME_ALREADY_EXISTS" in e.getrepr()
