from uuid import uuid4

import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_non_user_tasks(
    config,
    test_client: AsyncClient,
    status_assertion,
):
    resp = await test_client.get("/platform/tasks/user")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_user_tasks(
    config,
    test_client: AsyncClient,
    status_assertion,
    login,
):
    await login()
    resp = await test_client.get("/platform/tasks/user")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_all_tasks(
    config,
    test_client: AsyncClient,
    status_assertion,
    login,
):
    # as normal user (fails)
    await login()
    resp = await test_client.get("/platform/tasks")
    assert status_assertion(401, resp)

    # as admin
    await login(is_superuser=True)
    resp = await test_client.get("/platform/tasks")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_download_artifact(
    config,
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wait_for_task_success,
):
    await insert_sample_data()

    # request resource export
    resp = await test_client.get(
        "/resources/66471b68ba9e65342c8e495b/export",
        params={
            "format": "csv",
            "from": "654b825533ee5737b297f8e5",
            "to": "654b825533ee5737b297f8f2",
        },
    )
    assert status_assertion(202, resp)
    assert "id" in resp.json()
    assert "pickupKey" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])
    pickup_key = resp.json()["pickupKey"]

    # fail to download generated artifact with wrong pickup key
    resp = await test_client.get(
        "/platform/tasks/download",
        params={"pickupKey": uuid4().hex},
    )
    assert status_assertion(404, resp)

    # download generated artifact
    resp = await test_client.get(
        "/platform/tasks/download",
        params={"pickupKey": pickup_key},
    )
    assert status_assertion(200, resp)


@pytest.mark.anyio
async def test_delete_tasks(
    config,
    test_client: AsyncClient,
    insert_sample_data,
    status_assertion,
    wait_for_task_success,
    login,
):
    await insert_sample_data()
    await login(is_superuser=True)

    # start index creation task (to have a task to work with)
    resp = await test_client.get("/search/index/create")
    assert status_assertion(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["status"] == "done"

    # delete all system tasks
    resp = await test_client.delete("/platform/tasks/system")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1  # still 1 because it's not a system task

    # delete all tasks
    resp = await test_client.delete("/platform/tasks/all")
    assert status_assertion(204, resp)

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0
