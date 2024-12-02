import pytest

from httpx import AsyncClient
from tekst import package_metadata


@pytest.mark.anyio
async def test_platform_data(
    test_client: AsyncClient,
    status_assertion,
):
    resp = await test_client.get("/platform")
    assert status_assertion(200, resp)
    assert resp.json()["tekst"]["version"] == package_metadata["version"]


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
async def test_update_platform_settings(
    test_client: AsyncClient,
    status_assertion,
    login,
):
    await login(is_superuser=True)
    resp = await test_client.patch(
        "/platform/settings",
        json={"availableLocales": ["enUS"]},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "availableLocales" in resp.json()
    assert len(resp.json()["availableLocales"]) == 1
    assert resp.json()["availableLocales"][0] == "enUS"


@pytest.mark.anyio
async def test_get_public_user_info(
    test_client: AsyncClient,
    status_assertion,
    login,
    wrong_id,
):
    user = await login()
    resp = await test_client.get(f"/users/public/{user.get('id')}")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "username" in resp.json()
    assert resp.json()["username"] == user.get("username")
    # wrong user ID
    resp = await test_client.get(f"/platform/users/{wrong_id}")
    assert status_assertion(404, resp)


@pytest.mark.anyio
async def test_crud_segment(
    test_client: AsyncClient,
    status_assertion,
    login,
    wrong_id,
):
    await login(is_superuser=True)

    # create segment
    resp = await test_client.post(
        "/platform/segments",
        json={"key": "system_foo", "locale": "*", "title": "Foo", "html": "<p>Foo</p>"},
    )
    assert status_assertion(201, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Foo"
    segment_id = resp.json()["id"]

    # create conflicting segment
    resp = await test_client.post(
        "/platform/segments",
        json={"key": "system_foo", "locale": "*", "title": "Bar", "html": "<p>Bar</p>"},
    )
    assert status_assertion(409, resp)

    # update segment
    resp = await test_client.patch(
        f"/platform/segments/{segment_id}",
        json={"title": "Bar"},
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Bar"

    # update segment via wrong ID
    resp = await test_client.patch(
        f"/platform/segments/{wrong_id}",
        json={"title": "Bar"},
    )
    assert status_assertion(404, resp)

    # get segment
    resp = await test_client.get(
        f"/platform/segments/{segment_id}",
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Bar"

    # get segment via wrong ID
    resp = await test_client.get(
        f"/platform/segments/{wrong_id}",
    )
    assert status_assertion(404, resp)

    # delete segment
    resp = await test_client.delete(
        f"/platform/segments/{segment_id}",
    )
    assert status_assertion(204, resp)

    # delete segment via wrong ID
    resp = await test_client.delete(
        f"/platform/segments/{wrong_id}",
    )
    assert status_assertion(404, resp)
