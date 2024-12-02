import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_send_receive_messages(
    test_client: AsyncClient,
    status_assertion,
    insert_sample_data,
    login,
    wrong_id,
):
    await insert_sample_data()
    user = await login()
    target_sample_user_id = "65c5fe0c691066aabd498238"

    # send valid message
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": target_sample_user_id,
            "content": "This\nis\na\ntest.",
        },
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["sender"] == user["id"]

    # send another valid message
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": target_sample_user_id,
            "content": "FOO BAR",
        },
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["sender"] == user["id"]

    # send message to self
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": user["id"],
            "content": "This\nis\na\ntest.",
        },
    )
    assert status_assertion(400, resp)

    # send message to non-existent recipient
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": wrong_id,
            "content": "This\nis\na\ntest.",
        },
    )
    assert status_assertion(404, resp)

    # send message without content
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": target_sample_user_id,
            "content": "",
        },
    )
    assert status_assertion(422, resp)

    # get message threads
    resp = await test_client.get("/messages/threads")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == target_sample_user_id
    assert resp.json()[0]["contact"]["id"] == target_sample_user_id
    assert resp.json()[0]["unread"] == 0

    # get messages for specific thread
    resp = await test_client.get("/messages", params={"thread": resp.json()[0]["id"]})
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2
    assert resp.json()[0]["recipient"] == target_sample_user_id

    # fail to delete message thread w/ wrong ID
    resp = await test_client.delete(f"/messages/threads/{wrong_id}")
    assert status_assertion(404, resp)

    # delete message thread
    resp = await test_client.delete(f"/messages/threads/{target_sample_user_id}")
    assert status_assertion(204, resp)

    # get message threads (should be 0 now)
    resp = await test_client.get("/messages/threads")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0
