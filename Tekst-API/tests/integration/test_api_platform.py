import pytest

from httpx import AsyncClient
from tekst import pkg_meta


@pytest.mark.anyio
async def test_platform_data(api_path, test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get("/platform")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["tekst"]["version"] == pkg_meta["version"]


@pytest.mark.anyio
async def test_platform_users(
    reset_db,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    user = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(user)
    resp = await test_client.get(
        "/platform/users", params={"q": user.get("username")}, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["username"] == user["username"]
    assert "id" in resp.json()[0]
    assert "name" in resp.json()[0]
    assert "isActive" not in resp.json()[0]
    resp = await test_client.get(
        "/platform/users", params={"q": "nonsense"}, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_update_platform_settings(
    reset_db,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    user = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(user)
    resp = await test_client.patch(
        "/platform/settings",
        json={"availableLocales": ["enUS"]},
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "availableLocales" in resp.json()
    assert resp.json()["availableLocales"][0] == "enUS"


@pytest.mark.anyio
async def test_get_public_user_info(
    reset_db,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    user = await register_test_user()
    resp = await test_client.get(f"/platform/users/{user.get('id')}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "username" in resp.json()
    assert resp.json()["username"] == user.get("username")
