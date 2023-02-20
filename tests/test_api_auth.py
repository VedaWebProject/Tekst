import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register(
    root_path, test_client: AsyncClient, new_user_data, status_fail_msg
):
    endpoint = f"{root_path}/auth/register"
    payload = new_user_data()
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_register_invalid_pw(
    root_path, test_client: AsyncClient, new_user_data, status_fail_msg
):
    endpoint = f"{root_path}/auth/register"
    payload = new_user_data()

    payload["password"] = "foo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)

    payload["password"] = "foooooooooooo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)

    payload["password"] = "Fooooooooooo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)

    payload["password"] = "Foo1234"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_login(config, root_path, test_client: AsyncClient, status_fail_msg):
    # make an unsuspicious request to get the csrf token
    resp = await test_client.post(f"{root_path}/texts")
    # save csrf token from previous "safe" request
    # (which is the login request - all subsequent requests will contain the
    # auth cookie and are not considered safe)
    assert resp.cookies.get(config.security.csrf_cookie_name)
    csrf_token = resp.cookies.get(config.security.csrf_cookie_name)

    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "verified@test.com", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            config.security.csrf_header_name: csrf_token,
        },
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.cookies.get(config.security.auth_cookie_name)


@pytest.mark.anyio
async def test_login_fail_bad_pw(
    config, root_path, test_client: AsyncClient, status_fail_msg
):
    # make an unsuspicious request to get the csrf token
    resp = await test_client.post(f"{root_path}/texts")
    # save csrf token from previous "safe" request
    # (which is the login request - all subsequent requests will contain the
    # auth cookie and are not considered safe)
    assert resp.cookies.get(config.security.csrf_cookie_name)
    csrf_token = resp.cookies.get(config.security.csrf_cookie_name)

    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "verified@test.com", "password": "wrongpassword"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            config.security.csrf_header_name: csrf_token,
        },
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.anyio
async def test_login_fail_unverified(
    config, root_path, test_client: AsyncClient, status_fail_msg
):
    # make an unsuspicious request to get the csrf token
    resp = await test_client.post(f"{root_path}/texts")
    # save csrf token from previous "safe" request
    # (which is the login request - all subsequent requests will contain the
    # auth cookie and are not considered safe)
    assert resp.cookies.get(config.security.csrf_cookie_name)
    csrf_token = resp.cookies.get(config.security.csrf_cookie_name)

    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "unverified@test.com", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            config.security.csrf_header_name: csrf_token,
        },
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)
    assert resp.json()["detail"] == "LOGIN_USER_NOT_VERIFIED"


@pytest.mark.anyio
async def test_user_updates_self(
    config, root_path, test_client: AsyncClient, status_fail_msg
):
    # make an unsuspicious request to get the csrf token
    resp = await test_client.post(f"{root_path}/texts")
    # save csrf token from previous "safe" request
    # (which is the login request - all subsequent requests will contain the
    # auth cookie and are not considered safe)
    assert resp.cookies.get(config.security.csrf_cookie_name)
    csrf_token = resp.cookies.get(config.security.csrf_cookie_name)

    # login
    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "verified@test.com", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        cookies={config.security.csrf_cookie_name: csrf_token},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            config.security.csrf_header_name: csrf_token,
        },
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # save auth cookie
    assert resp.cookies.get(config.security.auth_cookie_name)
    auth_token = resp.cookies.get(config.security.auth_cookie_name)

    # get user data from /users/me
    endpoint = f"{root_path}/users/me"
    resp = await test_client.get(
        endpoint,
        cookies={
            config.security.auth_cookie_name: auth_token,
            config.security.csrf_cookie_name: csrf_token,
        },
        headers={config.security.csrf_header_name: csrf_token},
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
            config.security.csrf_cookie_name: csrf_token,
        },
        headers={config.security.csrf_header_name: csrf_token},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["id"] == user_id
    assert resp.json()["firstName"] == "Bird Person"
