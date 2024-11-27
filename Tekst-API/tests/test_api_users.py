import pytest

from fastapi.exceptions import HTTPException
from httpx import AsyncClient
from tekst.auth import create_initial_superuser


@pytest.mark.anyio
async def test_admin_get_all_users(
    test_client: AsyncClient,
    status_assertion,
    insert_sample_data,
    login,
):
    await insert_sample_data("users")
    await login(is_superuser=True)
    resp = await test_client.get("/users")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 5


@pytest.mark.anyio
async def test_find_users(
    test_client: AsyncClient,
    status_assertion,
    login,
):
    user = await login(is_superuser=True)

    # legitimate search
    resp = await test_client.get(
        "/users/public",
        params={"q": user.get("username")},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 1
    assert resp.json()["users"][0]["username"] == user["username"]
    assert "id" in resp.json()["users"][0]
    assert "name" in resp.json()["users"][0]
    assert "isVerified" not in resp.json()["users"][0]

    # nonsense search
    resp = await test_client.get(
        "/users/public",
        params={"q": "nonsense"},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0

    # no query, empty query = no results
    resp = await test_client.get(
        "/users/public",
        params={"emptyOk": False},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0

    # no query, empty query = all users
    resp = await test_client.get(
        "/users/public",
        params={"emptyOk": True},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) > 0

    # query of whitespaces
    resp = await test_client.get(
        "/users/public",
        params={"q": "      ", "emptyOk": False},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0


@pytest.mark.anyio
async def test_user_updates_self(
    login,
    test_client: AsyncClient,
    status_assertion,
):
    await login()
    # get user data from /users/me
    resp = await test_client.get(
        "/users/me",
    )
    assert status_assertion(200, resp)
    assert "id" in resp.json()
    # update own first name
    user_id = resp.json()["id"]
    updates = {"name": "Bird Person"}
    resp = await test_client.patch(
        "/users/me",
        json=updates,
    )
    assert status_assertion(200, resp)
    assert resp.json()["id"] == user_id
    assert resp.json()["name"] == "Bird Person"


@pytest.mark.anyio
async def test_user_deletes_self(
    login,
    test_client: AsyncClient,
    status_assertion,
):
    await login()
    # delete self
    resp = await test_client.delete(
        "/users/me",
    )
    assert status_assertion(204, resp)


@pytest.mark.anyio
async def test_update_user(
    login,
    register_test_user,
    test_client: AsyncClient,
    status_assertion,
):
    user = await register_test_user(is_active=False)
    await login(is_superuser=True)
    # update user
    resp = await test_client.patch(
        f"/users/{user['id']}",
        json={"isActive": True, "isSuperuser": True, "password": "XoiPOI09871"},
    )
    assert status_assertion(200, resp)
    assert resp.json()["isActive"] is True
    assert resp.json()["isSuperuser"] is True
    assert "password" not in resp.json()
    # update user again
    resp = await test_client.patch(
        f"/users/{user['id']}", json={"isActive": False, "isSuperuser": False}
    )
    assert status_assertion(200, resp)
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
