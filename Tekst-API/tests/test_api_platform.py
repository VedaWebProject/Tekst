from datetime import UTC, datetime, timedelta

import pytest

from beanie import PydanticObjectId
from beanie.operators import Eq, Set
from httpx import AsyncClient
from tekst import package_metadata
from tekst.auth import AccessTokenDocument
from tekst.models.content import ContentBaseDocument
from tekst.models.message import UserMessageDocument


@pytest.mark.anyio
async def test_platform_data(
    test_client: AsyncClient,
    assert_status,
    insert_test_data,
):
    await insert_test_data()
    resp = await test_client.get("/platform")
    assert_status(200, resp)
    assert resp.json()["tekst"]["version"] == package_metadata["version"]


@pytest.mark.anyio
async def test_web_init_data(
    test_client: AsyncClient,
    assert_status,
    insert_test_data,
    login,
):
    await insert_test_data()
    # anonymous
    resp = await test_client.get("/platform/web-init")
    assert_status(200, resp)
    assert "platform" in resp.json()
    assert "user" in resp.json()
    assert resp.json()["user"] is None
    assert len(resp.json()["platform"]["infoSegments"]) == 2
    # logged in
    await login()
    resp = await test_client.get("/platform/web-init")
    assert_status(200, resp)
    assert "user" in resp.json()
    assert resp.json()["user"] is not None
    assert len(resp.json()["platform"]["infoSegments"]) == 4
    # logged in as admin
    await login(is_superuser=True)
    resp = await test_client.get("/platform/web-init")
    assert_status(200, resp)
    assert "user" in resp.json()
    assert resp.json()["user"] is not None
    assert len(resp.json()["platform"]["infoSegments"]) == 6


@pytest.mark.anyio
async def test_update_platform_state(
    test_client: AsyncClient,
    assert_status,
    login,
):
    await login(is_superuser=True)
    resp = await test_client.patch(
        "/platform/state",
        json={"availableLocales": ["enUS"]},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "availableLocales" in resp.json()
    assert len(resp.json()["availableLocales"]) == 1
    assert resp.json()["availableLocales"][0] == "enUS"


@pytest.mark.anyio
async def test_update_pf_state_invalid_denied_res_type(
    test_client: AsyncClient,
    login,
    assert_status,
):
    await login(is_superuser=True)
    resp = await test_client.patch(
        "/platform/state",
        json={"denyResourceTypes": ["foo"]},
    )
    assert_status(422, resp)


@pytest.mark.anyio
async def test_crud_segment(
    test_client: AsyncClient,
    assert_status,
    login,
    wrong_id,
):
    await login(is_superuser=True)

    # create segment
    resp = await test_client.post(
        "/platform/segments",
        json={"key": "system_foo", "locale": "*", "title": "Foo", "html": "<p>Foo</p>"},
    )
    assert_status(201, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Foo"
    segment_id = resp.json()["id"]

    # create conflicting segment
    resp = await test_client.post(
        "/platform/segments",
        json={"key": "system_foo", "locale": "*", "title": "Bar", "html": "<p>Bar</p>"},
    )
    assert_status(409, resp)

    # update segment
    resp = await test_client.patch(
        f"/platform/segments/{segment_id}",
        json={"title": "Bar"},
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Bar"

    # update segment via wrong ID
    resp = await test_client.patch(
        f"/platform/segments/{wrong_id}",
        json={"title": "Bar"},
    )
    assert_status(404, resp)

    # get segment
    resp = await test_client.get(
        f"/platform/segments/{segment_id}",
    )
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "title" in resp.json()
    assert resp.json()["title"] == "Bar"

    # get segment via wrong ID
    resp = await test_client.get(
        f"/platform/segments/{wrong_id}",
    )
    assert_status(404, resp)

    # delete segment
    resp = await test_client.delete(
        f"/platform/segments/{segment_id}",
    )
    assert_status(204, resp)

    # delete segment via wrong ID
    resp = await test_client.delete(
        f"/platform/segments/{wrong_id}",
    )
    assert_status(404, resp)


@pytest.mark.anyio
async def test_platform_cleanup_access_tokens(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wait_for_task_success,
    config,
):
    await insert_test_data()
    await login()  # login as regular user

    # there should be 1 access token, now
    assert await AccessTokenDocument.find().count() == 1

    # manipulate all access tokens to be 20 hours old
    # (access token lifetime is set to 1 hour in tests config)
    await AccessTokenDocument.find().update(
        Set({AccessTokenDocument.created_at: datetime.now(UTC) - timedelta(hours=20)})
    )

    await login(is_superuser=True)  # login as superuser

    # there should be 2 access tokens, now
    assert await AccessTokenDocument.find().count() == 2

    # run cleanup
    resp = await test_client.get("/platform/cleanup")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # there should be 1 access token left, now
    assert await AccessTokenDocument.find().count() == 1


@pytest.mark.anyio
async def test_platform_cleanup_user_messages(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wait_for_task_success,
    config,
):
    await insert_test_data()
    await login(is_superuser=True)

    # create stale user message
    await UserMessageDocument(
        sender=PydanticObjectId("69c510aef0e54419806c7a24"),
        recipient=PydanticObjectId("69c510b8f0e54419806c7a25"),
        content="FOO BAR",
        created_at=(
            datetime.now(UTC)
            - timedelta(days=config.misc.usrmsg_force_delete_after_days + 1)
        ),
    ).save()

    # there should be 1 message, now
    assert await UserMessageDocument.find().count() == 1

    # run cleanup
    resp = await test_client.get("/platform/cleanup")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # there should be 0 messages left, now
    assert await UserMessageDocument.find().count() == 0


@pytest.mark.anyio
async def test_platform_cleanup_archive_duplicates(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wait_for_task_success,
    config,
):
    await insert_test_data()
    await login(is_superuser=True)

    # get a target content
    content = await ContentBaseDocument.get(
        PydanticObjectId("67c04798906e79b9062e2344"),
        with_children=True,
    )
    assert content

    # check that there are no archived versions for the target content, yet
    assert (
        await ContentBaseDocument.find(
            Eq(ContentBaseDocument.resource_id, content.resource_id),
            Eq(ContentBaseDocument.location_id, content.location_id),
            Eq(ContentBaseDocument.archived, True),
            with_children=True,
        ).count()
        == 0
    )

    # create archived versions of target content
    for i, text in enumerate(["a", "a", "a", "b", "c", "d", "e", "e", "e"]):
        await content.model_copy(
            update={
                "id": None,
                "text": text,
                "created_at": content.created_at - timedelta(days=i + 1),
                "archived": True,
            }
        ).save()

    # check archived contents count
    assert (
        await ContentBaseDocument.find(
            Eq(ContentBaseDocument.resource_id, content.resource_id),
            Eq(ContentBaseDocument.location_id, content.location_id),
            Eq(ContentBaseDocument.archived, True),
            with_children=True,
        ).count()
        == 9
    )

    # run cleanup
    resp = await test_client.get("/platform/cleanup")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # check archived contents
    # 5 of the 9 created should be left
    assert (
        "".join(
            [
                c.text
                for c in await ContentBaseDocument.find(
                    Eq(ContentBaseDocument.resource_id, content.resource_id),
                    Eq(ContentBaseDocument.location_id, content.location_id),
                    Eq(ContentBaseDocument.archived, True),
                    with_children=True,
                )
                .sort(-ContentBaseDocument.created_at)  # ty:ignore[unsupported-operator]
                .to_list()
            ]
        )
        == "abcde"
    )

    # run cleanup again
    resp = await test_client.get("/platform/cleanup")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # check archived contents count
    # again, 5 of the 9 created should be left
    assert (
        "".join(
            [
                c.text
                for c in await ContentBaseDocument.find(
                    Eq(ContentBaseDocument.resource_id, content.resource_id),
                    Eq(ContentBaseDocument.location_id, content.location_id),
                    Eq(ContentBaseDocument.archived, True),
                    with_children=True,
                )
                .sort(-ContentBaseDocument.created_at)  # ty:ignore[unsupported-operator]
                .to_list()
            ]
        )
        == "abcde"
    )


@pytest.mark.anyio
async def test_admin_test_email(
    test_client: AsyncClient,
    assert_status,
    login,
):
    await login(is_superuser=True)
    resp = await test_client.get("/platform/test-email")
    assert_status(204, resp)


@pytest.mark.anyio
async def test_get_stats(
    test_client: AsyncClient,
    assert_status,
    login,
):
    # as user
    await login()
    resp = await test_client.get("/platform/stats")
    assert_status(200, resp)
    assert "statsRequests" in resp.json()
    assert resp.json()["statsRequests"] == 0
    # as superuser
    await login(is_superuser=True)
    resp = await test_client.get("/platform/stats")
    assert_status(200, resp)
    assert "statsRequests" in resp.json()
    assert resp.json()["statsRequests"] == 1
