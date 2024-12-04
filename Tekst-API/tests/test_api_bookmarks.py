import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_crud_bookmark(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wrong_id,
    login,
):
    await insert_sample_data("texts", "locations", "resources")
    superuser = await login(is_superuser=True)
    location_id = "654b825533ee5737b297f8eb"  # hand-picked because we need a level 1 bm

    # fail to create bookmark with wrong location ID
    resp = await test_client.post(
        "/bookmarks",
        json={
            "locationId": wrong_id,
            "comment": "FOO",
        },
    )
    assert status_assertion(404, resp)

    # create bookmark
    resp = await test_client.post(
        "/bookmarks",
        json={
            "locationId": location_id,
            "comment": "FOO",
        },
    )
    assert status_assertion(201, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["comment"] == "FOO"
    assert "id" in resp.json()
    assert resp.json()["userId"] == superuser["id"]
    bookmark_id = resp.json()["id"]

    # create conflicting bookmark
    resp = await test_client.post(
        "/bookmarks",
        json={
            "locationId": location_id,
            "comment": "This should not work",
        },
    )
    assert status_assertion(409, resp)

    # get all user bookmarks
    resp = await test_client.get(
        "/bookmarks",
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert resp.json()[0]["comment"] == "FOO"

    # fail to delete with wrong ID
    resp = await test_client.delete(f"/bookmarks/{wrong_id}")
    assert status_assertion(404, resp)

    # fail to delete as wrong user
    await login()
    resp = await test_client.delete(f"/bookmarks/{bookmark_id}")
    assert status_assertion(403, resp)
    await login(user=superuser)

    # delete bookmark
    resp = await test_client.delete(f"/bookmarks/{bookmark_id}")
    assert status_assertion(204, resp)
