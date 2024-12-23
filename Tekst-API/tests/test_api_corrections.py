import pytest

from beanie import PydanticObjectId
from httpx import AsyncClient
from tekst.models.resource import ResourceBaseDocument


@pytest.mark.anyio
async def test_corrections_crud(
    test_client: AsyncClient,
    insert_sample_data,
    assert_status,
    login,
    wrong_id,
):
    await insert_sample_data()
    resource = await ResourceBaseDocument.find_one(with_children=True)
    res_id = str(resource.id)
    u = await login()

    # create correction note on public resource
    resp = await test_client.post(
        "/corrections",
        json={
            "resourceId": res_id,
            "position": 0,
            "note": "Something is wrong here.",
        },
    )
    assert_status(201, resp)

    # fail to create correction note with wrong resource ID
    resp = await test_client.post(
        "/corrections",
        json={
            "resourceId": wrong_id,
            "position": 0,
            "note": "Something is wrong here.",
        },
    )
    assert_status(404, resp)

    # fail to create correction note for invalid location
    resp = await test_client.post(
        "/corrections",
        json={
            "resourceId": res_id,
            "position": 9999,
            "note": "Something is wrong here.",
        },
    )
    assert_status(404, resp)

    # fail to get correction notes (because of missing permissions)
    resp = await test_client.get(f"/corrections/{res_id}")
    assert_status(404, resp)

    # log in as superuser (to be able to access corrections data)
    su = await login(is_superuser=True)

    # get correction notes
    resp = await test_client.get(f"/corrections/{res_id}")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["note"] == "Something is wrong here."
    correction_id = resp.json()[0]["id"]

    # fail to delete correction note with wrong ID
    resp = await test_client.delete(f"/corrections/{wrong_id}")
    assert_status(404, resp)

    # delete correction note
    resp = await test_client.delete(f"/corrections/{correction_id}")
    assert_status(204, resp)

    # get correction notes
    resp = await test_client.get(f"/corrections/{res_id}")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # create correction note on non-public resource (with specific owner)
    resource.owner_id = PydanticObjectId(u["id"])
    resource.public = False
    await resource.replace()
    resp = await test_client.post(
        "/corrections",
        json={
            "resourceId": res_id,
            "position": 0,
            "note": "This should trigger a notification to the resource owner.",
        },
    )
    assert_status(201, resp)
    assert isinstance(resp.json(), dict)
    assert "id" in resp.json()
    correction_id = resp.json()["id"]

    # fail to delete correction note with missing permissions
    resource.owner_id = PydanticObjectId(su["id"])
    await resource.replace()
    await login(user=u)  # logs out admin, logs in existing normal user
    resp = await test_client.delete(f"/corrections/{correction_id}")
    assert_status(404, resp)
