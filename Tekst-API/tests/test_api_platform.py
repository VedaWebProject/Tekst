import pytest

from httpx import AsyncClient
from tekst import package_metadata


@pytest.mark.anyio
async def test_platform_data(test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get("/platform")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["tekst"]["version"] == package_metadata["version"]


@pytest.mark.anyio
async def test_platform_find_users(
    test_client: AsyncClient,
    status_fail_msg,
    login,
):
    user = await login(is_superuser=True)

    # legitimate search
    resp = await test_client.get(
        "/users/public",
        params={"q": user.get("username")},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 1
    assert resp.json()["users"][0]["username"] == user["username"]
    assert "id" in resp.json()["users"][0]
    assert "name" in resp.json()["users"][0]
    assert "isVerified" not in resp.json()["users"][0]

    # nonsense search
    resp = await test_client.get(
        "/users/public",
        params={"q": "nonsense"},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0

    # no query, empty query = no results
    resp = await test_client.get(
        "/users/public",
        params={"emptyOk": False},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0

    # no query, empty query = all users
    resp = await test_client.get(
        "/users/public",
        params={"emptyOk": True},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) > 0

    # query of whitespaces
    resp = await test_client.get(
        "/users/public",
        params={"q": "      ", "emptyOk": False},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "users" in resp.json()
    assert len(resp.json()["users"]) == 0


@pytest.mark.anyio
async def test_update_platform_settings(
    test_client: AsyncClient,
    status_fail_msg,
    login,
):
    await login(is_superuser=True)
    resp = await test_client.patch(
        "/platform/settings",
        json={"availableLocales": ["enUS"]},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "availableLocales" in resp.json()
    assert len(resp.json()["availableLocales"]) == 1
    assert resp.json()["availableLocales"][0] == "enUS"


@pytest.mark.anyio
async def test_get_public_user_info(
    test_client: AsyncClient, status_fail_msg, login, wrong_id
):
    user = await login()
    resp = await test_client.get(f"/users/public/{user.get('id')}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "username" in resp.json()
    assert resp.json()["username"] == user.get("username")
    # wrong user ID
    resp = await test_client.get(f"/platform/users/{wrong_id}")
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_crud_segment(
    test_client: AsyncClient,
    status_fail_msg,
    login,
    wrong_id,
):
    await login(is_superuser=True)

    # create segment
    resp = await test_client.post(
        "/platform/segments",
        json={"key": "system_foo", "locale": "*", "title": "Foo", "html": "<p>Foo</p>"},
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Foo"
    segment_id = resp.json()["id"]

    # create conflicting segment
    resp = await test_client.post(
        "/platform/segments",
        json={"key": "system_foo", "locale": "*", "title": "Bar", "html": "<p>Bar</p>"},
    )
    assert resp.status_code == 409, status_fail_msg(409, resp)

    # update segment
    resp = await test_client.patch(
        f"/platform/segments/{segment_id}",
        json={"title": "Bar"},
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Bar"

    # update segment via wrong ID
    resp = await test_client.patch(
        f"/platform/segments/{wrong_id}",
        json={"title": "Bar"},
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # get segment
    resp = await test_client.get(
        f"/platform/segments/{segment_id}",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Bar"

    # get segment via wrong ID
    resp = await test_client.get(
        f"/platform/segments/{wrong_id}",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # delete segment
    resp = await test_client.delete(
        f"/platform/segments/{segment_id}",
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)

    # delete segment via wrong ID
    resp = await test_client.delete(
        f"/platform/segments/{wrong_id}",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)
