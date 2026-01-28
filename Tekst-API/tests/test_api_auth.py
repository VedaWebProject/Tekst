import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_register(
    insert_test_data,
    test_client: AsyncClient,
    get_mock_user,
    assert_status,
):
    await insert_test_data()  # to have an admin to notify after registration
    payload = get_mock_user()
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(201, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_register_invalid_pw(
    test_client: AsyncClient,
    get_mock_user,
    assert_status,
    clear_db,
):
    payload = get_mock_user()

    payload["password"] = f"aA1{payload['email']}0oO"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "uuuuhhh"
    payload["password"] = "foo"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "aaaa"
    payload["password"] = "foooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "bbbb"
    payload["password"] = "Fooooooooooo"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"

    payload["username"] = "cccc"
    payload["password"] = "Foo1234"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(400, resp)
    assert resp.json()["detail"]["code"] == "REGISTER_INVALID_PASSWORD"


@pytest.mark.anyio
async def test_register_username_exists(
    test_client: AsyncClient,
    get_mock_user,
    assert_status,
    clear_db,
):
    payload = get_mock_user()

    payload["username"] = "someuser"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(201, resp)

    payload["email"] = "hello@hello.com"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(400, resp)


@pytest.mark.anyio
async def test_register_email_exists(
    test_client: AsyncClient,
    get_mock_user,
    assert_status,
    clear_db,
):
    payload = get_mock_user()

    payload["email"] = "first@tekst.dev"
    payload["username"] = "first"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(201, resp)

    payload["username"] = "second"
    resp = await test_client.post("/auth/register", json=payload)
    assert_status(400, resp)
    assert resp.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS"


@pytest.mark.anyio
async def test_login_session_cookie(
    config,
    register_test_user,
    test_client: AsyncClient,
    assert_status,
    clear_db,
):
    user = await register_test_user()
    payload = {
        "username": user["email"],
        "password": user["password"],
        "persistent": False,
    }
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert_status(204, resp)
    assert resp.headers.get("set-cookie")
    assert "max-age" not in resp.headers.get("set-cookie").lower()
    assert "expires" not in resp.headers.get("set-cookie").lower()


@pytest.mark.anyio
async def test_login_persistent_cookie(
    config,
    register_test_user,
    test_client: AsyncClient,
    assert_status,
    clear_db,
):
    user = await register_test_user()
    payload = {
        "username": user["email"],
        "password": user["password"],
        "persistent": True,
    }
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert_status(204, resp)
    assert resp.headers.get("set-cookie")
    assert "max-age" in resp.headers.get("set-cookie").lower()


@pytest.mark.anyio
async def test_login_fail_bad_pw(
    login,
    test_client: AsyncClient,
    assert_status,
):
    user = await login()
    payload = {"username": user["username"], "password": "XoiPOI09871"}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert_status(400, resp)
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.anyio
async def test_login_fail_unverified(
    register_test_user,
    test_client: AsyncClient,
    assert_status,
    clear_db,
):
    user = await register_test_user(is_verified=False)
    payload = {"username": user["email"], "password": user["password"]}
    resp = await test_client.post(
        "/auth/cookie/login",
        data=payload,
    )
    assert_status(400, resp)
    assert resp.json()["detail"] == "LOGIN_USER_NOT_VERIFIED"


@pytest.mark.anyio
async def test_forgot_reset_password(
    register_test_user,
    test_client: AsyncClient,
    assert_status,
    get_emails,
):
    user = await register_test_user()

    # get all emails
    emails = await get_emails(2)
    assert isinstance(emails, dict)

    # report forgotten password
    resp = await test_client.post(
        "/auth/forgot-password",
        json={"email": user["email"]},
    )
    assert_status(202, resp)

    # check emails
    emails_count_before = len(emails["messages"])
    emails = await get_emails()
    print(emails)
    assert len(emails["messages"]) == emails_count_before + 1

    # reset password
    token = emails["messages"][0]["HTML"].split("token=")[1].split('"')[0]
    new_password = "oiuOIU876"
    resp = await test_client.post(
        "/auth/reset-password",
        json={"token": token, "password": new_password},
    )
    assert_status(200, resp)

    # check emails
    emails_count_before = len(emails["messages"])
    emails = await get_emails()
    assert len(emails["messages"]) == emails_count_before + 1
