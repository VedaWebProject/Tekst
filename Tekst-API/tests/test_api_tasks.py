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
    wait_for_task_success,
):
    await login()

    # get user tasks (none yet)
    resp = await test_client.get("/platform/tasks/user")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

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
    task_id = resp.json()["id"]

    # wait for task to finish (to make sure it's "done" before requesting tasks again)
    wait_for_task_success(task_id)

    # get user tasks (one now, requesting it deletes the "done" task)
    resp = await test_client.get("/platform/tasks/user")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1

    # get user tasks (no tasks anymore)
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

    # delete all tasks
    resp = await test_client.delete("/platform/tasks")
    assert status_assertion(204, resp)

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

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

    # delete specific task
    resp = await test_client.delete(f"/platform/tasks/{resp.json()[0]['id']}")
    assert status_assertion(204, resp)

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_tasks_locking(
    config,
    test_client: AsyncClient,
    status_assertion,
    insert_sample_data,
    login,
    wait_for_task_success,
):
    await insert_sample_data()
    await login(is_superuser=True)
    resp1 = await test_client.get("/search/index/create")
    resp2 = await test_client.get("/search/index/create")
    assert status_assertion(202, resp1)
    assert status_assertion(202, resp2)
    assert "id" in resp1.json()
    assert "id" in resp2.json()
    assert await wait_for_task_success(resp1.json()["id"])
    assert not await wait_for_task_success(resp2.json()["id"])
