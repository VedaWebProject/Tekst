import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_register(
    insert_sample_data,
    test_client: AsyncClient,
    get_fake_user,
    status_assertion,
):
    await insert_sample_data()  # to have an admin to notify after registration
    payload = get_fake_user()
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(201, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_register_invalid_pw(
    test_client: AsyncClient,
    get_fake_user,
    status_assertion,
):
    payload = get_fake_user()

    payload["password"] = f"aA1{payload['email']}0oO"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "uuuuhhh"
    payload["password"] = "foo"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "aaaa"
    payload["password"] = "foooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "bbbb"
    payload["password"] = "Fooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "cccc"
    payload["password"] = "Foo1234"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"


@pytest.mark.anyio
async def test_register_username_exists(
    test_client: AsyncClient,
    get_fake_user,
    status_assertion,
):
    payload = get_fake_user()

    payload["username"] = "someuser"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(201, resp)

    payload["email"] = "hello@hello.com"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(400, resp)


@pytest.mark.anyio
async def test_register_email_exists(
    test_client: AsyncClient,
    get_fake_user,
    status_assertion,
):
    payload = get_fake_user()

    payload["email"] = "first@tekst.dev"
    payload["username"] = "first"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(201, resp)

    payload["username"] = "second"
    resp = await test_client.post("/auth/register", json=payload)
    assert status_assertion(400, resp)
    assert resp.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS"


@pytest.mark.anyio
async def test_login(
    config,
    login,
    test_client: AsyncClient,
    status_assertion,
):
    user = await login()
    payload = {"username": user["email"], "password": user["password"]}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert status_assertion(204, resp)
    assert resp.cookies.get(config.security.auth_cookie_name)


@pytest.mark.anyio
async def test_login_fail_bad_pw(
    login,
    test_client: AsyncClient,
    status_assertion,
):
    user = await login()
    payload = {"username": user["username"], "password": "XoiPOI09871"}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert status_assertion(400, resp)
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.anyio
async def test_login_fail_unverified(
    register_test_user,
    test_client: AsyncClient,
    status_assertion,
):
    user = await register_test_user(is_verified=False)
    payload = {"username": user["email"], "password": user["password"]}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert status_assertion(400, resp)
    assert resp.json()["detail"] == "LOGIN_USER_NOT_VERIFIED"


@pytest.mark.anyio
async def test_forgot_password(
    login,
    test_client: AsyncClient,
    status_assertion,
):
    user = await login(is_active=True, is_verified=True)
    resp = await test_client.post(
        "/auth/forgot-password",
        json={"email": user["email"]},
    )
    assert status_assertion(202, resp)
