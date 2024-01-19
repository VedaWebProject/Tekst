import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_stats(
    test_client: AsyncClient,
    status_fail_msg,
    login,
    insert_sample_data,
):
    await insert_sample_data("texts", "nodes", "resources", "contents")
    await login(is_superuser=True)
    resp = await test_client.get("/admin/stats")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "usersCount" in resp.json()
    assert resp.json()["usersCount"] == 1


@pytest.mark.anyio
async def test_get_users(
    test_client: AsyncClient,
    status_fail_msg,
    login,
):
    superuser = await login(is_superuser=True)
    resp = await test_client.get("/admin/users")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["username"] == superuser["username"]
