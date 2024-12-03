import pytest

from httpx import AsyncClient
from tekst.models.resource import ResourceBaseDocument


@pytest.mark.anyio
async def test_corrections_crud(
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    login,
):
    await insert_sample_data()
    resource = await ResourceBaseDocument.find_one(with_children=True)
    await login()

    # create correction note
    resp = await test_client.post(
        "/corrections",
        json={
            "resourceId": str(resource.id),
            "position": 0,
            "note": "Something is wrong here.",
        },
    )
    assert status_assertion(201, resp)

    # fail to get correction notes (because of missing permissions)
    resp = await test_client.get(f"/corrections/{str(resource.id)}")
    assert status_assertion(404, resp)

    # log in as superuser (to be able to access corrections data)
    await login(is_superuser=True)

    # get correction notes
    resp = await test_client.get(f"/corrections/{str(resource.id)}")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["note"] == "Something is wrong here."
    correction_id = resp.json()[0]["id"]

    # delete correction note
    resp = await test_client.delete(f"/corrections/{correction_id}")
    assert status_assertion(204, resp)

    # get correction notes
    resp = await test_client.get(f"/corrections/{str(resource.id)}")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0
