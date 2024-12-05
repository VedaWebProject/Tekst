import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_messages_crud(
    test_client: AsyncClient,
    status_assertion,
    insert_sample_data,
    register_test_user,
    login,
    wrong_id,
):
    await insert_sample_data()
    su = await register_test_user(is_superuser=True)  # will be msg recipient
    u = await login()  # will be sending messages

    # send valid message
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": su["id"],
            "content": "This\nis\na\ntest.",
        },
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["sender"] == u["id"]

    # send another valid message
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": su["id"],
            "content": "FOO BAR",
        },
    )
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["sender"] == u["id"]

    # send message to self
    resp = await test_client.post(
        "/messages",
        json={
            "recipient": u["id"],
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
            "recipient": su["id"],
            "content": "",
        },
    )
    assert status_assertion(422, resp)

    # get message threads
    resp = await test_client.get("/messages/threads")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == su["id"]
    assert resp.json()[0]["contact"]["id"] == su["id"]
    assert resp.json()[0]["unread"] == 0

    # get messages for specific thread
    resp = await test_client.get("/messages", params={"thread": su["id"]})
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2
    assert resp.json()[0]["recipient"] == su["id"]

    # fail to delete message thread w/ wrong ID
    resp = await test_client.delete(f"/messages/threads/{wrong_id}")
    assert status_assertion(404, resp)

    # delete message thread
    resp = await test_client.delete(f"/messages/threads/{su['id']}")
    assert status_assertion(204, resp)

    # get message threads (should be 0 now)
    resp = await test_client.get("/messages/threads")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0

    # login as recipient user (now the other side of the convo)
    await login(user=su)

    # get message threads
    resp = await test_client.get("/messages/threads")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == u["id"]
    assert resp.json()[0]["contact"]["id"] == u["id"]
    assert resp.json()[0]["unread"] == 2

    # get messages for specific thread
    resp = await test_client.get("/messages", params={"thread": u["id"]})
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2
    assert resp.json()[0]["sender"] == u["id"]

    # get message threads (should have 0 unread messages now)
    resp = await test_client.get("/messages/threads")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == u["id"]
    assert resp.json()[0]["contact"]["id"] == u["id"]
    assert resp.json()[0]["unread"] == 0

    # delete message thread
    resp = await test_client.delete(f"/messages/threads/{u['id']}")
    assert status_assertion(204, resp)

    # get message threads (should be none left now)
    resp = await test_client.get("/messages/threads")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 0
