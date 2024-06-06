import pytest

from fastapi.exceptions import HTTPException
from httpx import AsyncClient
from tekst.auth import create_initial_superuser


@pytest.mark.anyio
async def test_register(test_client: AsyncClient, get_fake_user, status_fail_msg):
    payload = get_fake_user()
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_register_invalid_pw(
    test_client: AsyncClient, get_fake_user, status_fail_msg
):
    payload = get_fake_user()

    payload["password"] = f"aA1{payload['email']}0oO"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "uuuuhhh"
    payload["password"] = "foo"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "aaaa"
    payload["password"] = "foooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "bbbb"
    payload["password"] = "Fooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "cccc"
    payload["password"] = "Foo1234"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"


@pytest.mark.anyio
async def test_register_username_exists(
    test_client: AsyncClient, get_fake_user, status_fail_msg
):
    payload = get_fake_user()

    payload["username"] = "someuser"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)

    payload["email"] = "hello@hello.com"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_register_email_exists(
    test_client: AsyncClient, get_fake_user, status_fail_msg
):
    payload = get_fake_user()

    payload["email"] = "first@test.com"
    payload["username"] = "first"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)

    payload["username"] = "second"
    resp = await test_client.post("/auth/register", json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS"


@pytest.mark.anyio
async def test_login(
    config,
    login,
    test_client: AsyncClient,
    status_fail_msg,
):
    user = await login()
    payload = {"username": user["email"], "password": user["password"]}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)
    assert resp.cookies.get(config.security.auth_cookie_name)


@pytest.mark.anyio
async def test_login_fail_bad_pw(
    login,
    test_client: AsyncClient,
    status_fail_msg,
):
    user = await login()
    payload = {"username": user["username"], "password": "XoiPOI09871"}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.anyio
async def test_login_fail_unverified(
    register_test_user,
    test_client: AsyncClient,
    status_fail_msg,
):
    user = await register_test_user(is_verified=False)
    payload = {"username": user["email"], "password": user["password"]}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_USER_NOT_VERIFIED"


@pytest.mark.anyio
async def test_forgot_password(login, test_client: AsyncClient, status_fail_msg):
    user = await login(is_active=True, is_verified=True)
    resp = await test_client.post(
        "/auth/forgot-password",
        json={"email": user["email"]},
    )
    assert resp.status_code == 202, status_fail_msg(202, resp)


@pytest.mark.anyio
async def test_user_updates_self(
    login,
    test_client: AsyncClient,
    status_fail_msg,
):
    await login()
    # get user data from /users/me
    resp = await test_client.get(
        "/users/me",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    # update own first name
    user_id = resp.json()["id"]
    updates = {"name": "Bird Person"}
    resp = await test_client.patch(
        "/users/me",
        json=updates,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["id"] == user_id
    assert resp.json()["name"] == "Bird Person"


@pytest.mark.anyio
async def test_user_deletes_self(
    login,
    test_client: AsyncClient,
    status_fail_msg,
):
    await login()
    # delete self
    resp = await test_client.delete(
        "/users/me",
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)


@pytest.mark.anyio
async def test_update_user(
    login,
    register_test_user,
    test_client: AsyncClient,
    status_fail_msg,
):
    user = await register_test_user(is_active=False)
    await login(is_superuser=True)
    # update user
    resp = await test_client.patch(
        f"/users/{user['id']}",
        json={"isActive": True, "isSuperuser": True, "password": "XoiPOI09871"},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["isActive"] is True
    assert resp.json()["isSuperuser"] is True
    assert "password" not in resp.json()
    # update user again
    resp = await test_client.patch(
        f"/users/{user['id']}", json={"isActive": False, "isSuperuser": False}
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
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
