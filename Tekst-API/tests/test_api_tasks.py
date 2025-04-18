import asyncio

from uuid import uuid4

import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_non_user_tasks(
    config,
    test_client: AsyncClient,
    assert_status,
    wait_for_task_success,
    insert_test_data,
):
    await insert_test_data()

    # get (non-)user tasks (none, no pickup keys)
    resp = await test_client.get("/platform/tasks/user")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # request resource export
    resp = await test_client.get(
        "/resources/67c043c0906e79b9062e22f4/export",
        params={
            "format": "csv",
            "from": "67c040a0906e79b9062e22e8",
            "to": "67c042cf906e79b9062e22ed",
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    task_id = resp.json()["id"]
    pickup_key = resp.json()["pickupKey"]

    # wait for task to finish (to make sure it's "done" before requesting tasks again)
    await wait_for_task_success(task_id)

    # get (non-)user tasks
    # (one now, requesting it does not delete the task as it produced an artifact)
    resp = await test_client.get(
        "/platform/tasks/user",
        headers={"pickup-keys": pickup_key},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == task_id
    assert resp.json()[0]["status"] == "done"

    # download generated artifact
    resp = await test_client.get(
        "/platform/tasks/download",
        params={"pickupKey": pickup_key},
    )
    assert_status(200, resp)

    # wait a bit because task deletion after download is async
    await asyncio.sleep(2)

    # get (non-)user tasks
    # (no tasks anymore, as task got deleted when artifact was downloaded)
    resp = await test_client.get(
        "/platform/tasks/user",
        headers={"pickup-keys": pickup_key},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_user_tasks(
    config,
    test_client: AsyncClient,
    assert_status,
    login,
    wait_for_task_success,
    insert_test_data,
):
    await insert_test_data()
    await login(is_superuser=True)

    # get user tasks (none yet)
    resp = await test_client.get("/platform/tasks/user")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # create task to create index (to have a task to work with)
    resp = await test_client.get("/search/index/create")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get user tasks
    # (one now should be deleted on requesting tasks as it's
    # not a task that produced an artifact)
    resp = await test_client.get("/platform/tasks/user")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["status"] == "done"

    # get user tasks
    # (no tasks anymore, as task got deleted)
    resp = await test_client.get("/platform/tasks/user")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_get_all_tasks(
    config,
    test_client: AsyncClient,
    assert_status,
    login,
):
    # as normal user (fails)
    await login()
    resp = await test_client.get("/platform/tasks")
    assert_status(403, resp)

    # as admin
    await login(is_superuser=True)
    resp = await test_client.get("/platform/tasks")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_download_artifact(
    config,
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    wait_for_task_success,
):
    await insert_test_data()

    # request resource export
    resp = await test_client.get(
        "/resources/67c043c0906e79b9062e22f4/export",
        params={
            "format": "csv",
            "from": "654b825533ee5737b297f8e5",
            "to": "654b825533ee5737b297f8f2",
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert "pickupKey" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])
    pickup_key = resp.json()["pickupKey"]

    # fail to download generated artifact with wrong pickup key
    resp = await test_client.get(
        "/platform/tasks/download",
        params={"pickupKey": uuid4().hex},
    )
    assert_status(404, resp)

    # download generated artifact
    resp = await test_client.get(
        "/platform/tasks/download",
        params={"pickupKey": pickup_key},
    )
    assert_status(200, resp)


@pytest.mark.anyio
async def test_delete_tasks(
    config,
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    wait_for_task_success,
    login,
):
    await insert_test_data()
    await login(is_superuser=True)

    # start index creation task (to have a task to work with)
    resp = await test_client.get("/search/index/create")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["status"] == "done"

    # delete all tasks
    resp = await test_client.delete("/platform/tasks")
    assert_status(204, resp)

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # start index creation task (to have a task to work with)
    resp = await test_client.get("/search/index/create")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1

    # delete specific task
    resp = await test_client.delete(f"/platform/tasks/{resp.json()[0]['id']}")
    assert_status(204, resp)

    # get all tasks
    resp = await test_client.get("/platform/tasks")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0


@pytest.mark.anyio
async def test_tasks_locking(
    config,
    test_client: AsyncClient,
    assert_status,
    insert_test_data,
    login,
    wait_for_task_success,
):
    await insert_test_data()
    await login(is_superuser=True)
    resp1 = await test_client.get("/search/index/create")
    resp2 = await test_client.get("/search/index/create")
    assert resp1.status_code == 202
    assert resp2.status_code == 202
    assert "id" in resp1.json()
    assert "id" in resp2.json()
    assert await wait_for_task_success(resp1.json()["id"])
    assert not await wait_for_task_success(resp2.json()["id"])
