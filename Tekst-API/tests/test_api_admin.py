import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_stats(
    test_client: AsyncClient,
    status_assertion,
    login,
    insert_sample_data,
):
    await insert_sample_data("texts", "locations", "resources", "contents")
    await login(is_superuser=True)
    resp = await test_client.get("/platform/stats")
    assert status_assertion(200, resp)
    assert "usersCount" in resp.json()
    assert resp.json()["usersCount"] == 1


@pytest.mark.anyio
async def test_get_users(
    test_client: AsyncClient,
    status_assertion,
    login,
):
    superuser = await login(is_superuser=True)
    resp = await test_client.get("/users")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 1
    assert resp.json()["users"][0]["username"] == superuser["username"]
