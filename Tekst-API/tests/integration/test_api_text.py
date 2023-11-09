import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_texts(
    api_path, test_client: AsyncClient, insert_sample_data, status_fail_msg
):
    await insert_sample_data("texts")
    resp = await test_client.get("/texts")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    text_id = resp.json()[0]["id"]
    # get one by specific id
    resp = await test_client.get(f"/texts/{text_id}")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert resp.json()["id"] == text_id
    # get one by non-existent id
    resp = await test_client.get("/texts/637b9ad396d541a505e5439b")
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_create_text(
    reset_db,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)
    payload = {
        "title": "Just a Test",
        "slug": "justatest",
        "levels": [[{"locale": "enUS", "label": "foo"}]],
    }
    resp = await test_client.post("/texts", json=payload, cookies=session_cookie)
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
    # create duplicate
    resp = await test_client.post("/texts", json=payload, cookies=session_cookie)
    assert resp.status_code == 409, status_fail_msg(409, resp)


@pytest.mark.anyio
async def test_create_text_unauthorized(
    reset_db,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    user_data = await register_test_user()  # not a superuser (=unauthorized)!
    session_cookie = await get_session_cookie(user_data)
    payload = {"title": "Meow", "slug": "meow", "levels": ["meow"]}
    resp = await test_client.post("/texts", json=payload, cookies=session_cookie)
    assert resp.status_code == 403, status_fail_msg(403, resp)


@pytest.mark.anyio
async def test_create_text_unauthenticated(
    reset_db,
    api_path,
    test_client: AsyncClient,
    status_fail_msg,
):
    payload = {"title": "Meow", "slug": "meow", "levels": ["meow"]}
    resp = await test_client.post("/texts", json=payload)
    assert resp.status_code == 401, status_fail_msg(401, resp)


@pytest.mark.anyio
async def test_update_text(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    await insert_sample_data("texts")
    # get text from db
    resp = await test_client.get("/texts")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    text = resp.json()[0]
    # update text unauthenticated
    text_update = {"title": "Unauthenticated text update"}
    resp = await test_client.patch(f"/texts/{text['id']}", json=text_update)
    assert resp.status_code == 401, status_fail_msg(401, resp)
    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)
    # update text
    text_update = {"title": "Another text"}
    resp = await test_client.patch(
        f"/texts/{text['id']}", json=text_update, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(text["id"])
    assert "title" in resp.json()
    assert resp.json()["title"] == "Another text"
    # update unchanged text
    resp = await test_client.patch(
        f"/texts/{text['id']}", json=text_update, cookies=session_cookie
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    # update invalid text
    text_update = {"title": "Yet another text"}
    resp = await test_client.patch(
        "/texts/637b9ad396d541a505e5439b", json=text_update, cookies=session_cookie
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_insert_level(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    await insert_sample_data("texts")

    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)

    # get text from db
    resp = await test_client.get("/texts")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    text = resp.json()[0]
    assert len(text["levels"]) == 2

    # insert level
    resp = await test_client.post(
        f"/texts/{text['id']}/level/0",
        json=[
            {"locale": "enUS", "label": "A level"},
            {"locale": "deDE", "label": "Eine Ebene"},
        ],
        cookies=session_cookie,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert len(resp.json()["levels"]) == 3


@pytest.mark.anyio
async def test_upload_structure(
    api_path,
    test_client: AsyncClient,
    insert_sample_data,
    get_sample_data_path,
    status_fail_msg,
    register_test_user,
    get_session_cookie,
):
    text_id = (await insert_sample_data("texts"))["texts"][0]

    # create superuser
    superuser_data = await register_test_user(is_superuser=True)
    session_cookie = await get_session_cookie(superuser_data)

    # read structure file content
    with open(get_sample_data_path("structure/fdhdgg.json"), "rb") as f:
        # upload structure definition
        resp = await test_client.post(
            f"/texts/{text_id}/structure",
            cookies=session_cookie,
            files={"file": (f.name, f, "application/json")},
        )

    assert resp.status_code == 201, status_fail_msg(201, resp)
