import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_register(
    api_path, test_client: AsyncClient, new_user_data, status_fail_msg
):
    endpoint = f"{api_path}/auth/register"
    payload = new_user_data
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_register_invalid_pw(
    api_path, reset_db, test_client: AsyncClient, new_user_data, status_fail_msg
):
    endpoint = f"{api_path}/auth/register"
    payload = new_user_data

    payload["username"] = "uuuuhhh"
    payload["password"] = "foo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "aaaa"
    payload["password"] = "foooooooooooo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "bbbb"
    payload["password"] = "Fooooooooooo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "cccc"
    payload["password"] = "Foo1234"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"


@pytest.mark.anyio
async def test_register_username_exists(
    api_path, reset_db, test_client: AsyncClient, new_user_data, status_fail_msg
):
    endpoint = f"{api_path}/auth/register"
    payload = new_user_data

    payload["username"] = "someuser"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)

    payload["email"] = "hello@hello.com"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_register_email_exists(
    api_path, reset_db, test_client: AsyncClient, new_user_data, status_fail_msg
):
    endpoint = f"{api_path}/auth/register"
    payload = new_user_data

    payload["email"] = "first@test.com"
    payload["username"] = "first"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)

    payload["username"] = "second"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS"


@pytest.mark.anyio
async def test_login(
    config,
    reset_db,
    register_test_user,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
):
    await register_test_user()
    endpoint = f"{api_path}/auth/cookie/login"
    payload = {"username": "foo@bar.de", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)
    assert resp.cookies.get(config.security.auth_cookie_name)


@pytest.mark.anyio
async def test_login_fail_bad_pw(
    config,
    reset_db,
    register_test_user,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
):
    await register_test_user()
    endpoint = f"{api_path}/auth/cookie/login"
    payload = {"username": "foo@bar.de", "password": "wrongpassword"}
    resp = await test_client.post(
        endpoint,
        data=payload,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.anyio
async def test_login_fail_unverified(
    config,
    reset_db,
    register_test_user,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
):
    await register_test_user(is_verified=False)
    endpoint = f"{api_path}/auth/cookie/login"
    payload = {"username": "foo@bar.de", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_USER_NOT_VERIFIED"


@pytest.mark.anyio
async def test_user_updates_self(
    config,
    reset_db,
    register_test_user,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
):
    await register_test_user()
    # login
    endpoint = f"{api_path}/auth/cookie/login"
    payload = {"username": "foo@bar.de", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)

    # save auth cookie
    assert resp.cookies.get(config.security.auth_cookie_name)
    auth_token = resp.cookies.get(config.security.auth_cookie_name)

    # get user data from /users/me
    endpoint = f"{api_path}/users/me"
    resp = await test_client.get(
        endpoint,
        cookies={
            config.security.auth_cookie_name: auth_token,
        },
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()

    # update own first name
    user_id = resp.json()["id"]
    updates = {"firstName": "Bird Person"}
    resp = await test_client.patch(
        endpoint,
        json=updates,
        cookies={
            config.security.auth_cookie_name: auth_token,
        },
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["id"] == user_id
    assert resp.json()["firstName"] == "Bird Person"
