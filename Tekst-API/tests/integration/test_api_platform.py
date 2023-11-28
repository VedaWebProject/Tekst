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
    resp = await test_client.get("/platform/users", cookies=session_cookie)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["username"] == user["username"]
    assert "id" in resp.json()[0]
    assert "firstName" in resp.json()[0]
    assert "isActive" not in resp.json()[0]
