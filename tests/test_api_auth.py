import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register(root_path, test_client: AsyncClient, new_user_data):
    endpoint = f"{root_path}/auth/register"
    payload = new_user_data()
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 201, f"HTTP {resp.status_code} != 201 ({resp.json()})"
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_register_invalid_pw(root_path, test_client: AsyncClient, new_user_data):
    endpoint = f"{root_path}/auth/register"
    payload = new_user_data()

    payload["password"] = "foo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, f"HTTP {resp.status_code} != 400 ({resp.json()})"

    payload["password"] = "foooooooooooo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, f"HTTP {resp.status_code} != 400 ({resp.json()})"

    payload["password"] = "Fooooooooooo"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, f"HTTP {resp.status_code} != 400 ({resp.json()})"

    payload["password"] = "Foo1234"
    resp = await test_client.post(endpoint, json=payload)
    assert resp.status_code == 400, f"HTTP {resp.status_code} != 400 ({resp.json()})"


@pytest.mark.anyio
async def test_login(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "verified@test.com", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert resp.headers.get("Set-Cookie", False)


@pytest.mark.anyio
async def test_login_fail_bad_pw(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "verified@test.com", "password": "wrongpassword"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 400, f"HTTP {resp.status_code} != 400 ({resp.json()})"
    assert resp.json()["detail"] == "LOGIN_BAD_CREDENTIALS"


@pytest.mark.anyio
async def test_login_fail_unverified(root_path, test_client: AsyncClient):
    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "unverified@test.com", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 400, f"HTTP {resp.status_code} != 400 ({resp.json()})"
    assert resp.json()["detail"] == "LOGIN_USER_NOT_VERIFIED"


@pytest.mark.anyio
async def test_user_updates_self(root_path, test_client: AsyncClient):
    # login
    endpoint = f"{root_path}/auth/cookie/login"
    payload = {"username": "verified@test.com", "password": "poiPOI098"}
    resp = await test_client.post(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert resp.headers.get("Set-Cookie", False)

    # get user data from /users/me
    cookie = resp.headers.get("Set-Cookie")
    endpoint = f"{root_path}/users/me"
    resp = await test_client.get(endpoint, headers={"Cookie": cookie})
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert "id" in resp.json()

    # update own first name
    user_id = resp.json()["id"]
    updates = {"firstName": "Bird Person"}
    resp = await test_client.patch(endpoint, json=updates, headers={"Cookie": cookie})
    assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
    assert resp.json()["id"] == user_id
    assert resp.json()["firstName"] == "Bird Person"
