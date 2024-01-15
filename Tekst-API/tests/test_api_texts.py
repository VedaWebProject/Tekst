import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_texts(test_client: AsyncClient, insert_sample_data, status_fail_msg):
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
    test_client: AsyncClient,
    status_fail_msg,
    login,
):
    await login(is_superuser=True)
    payload = {
        "title": "Just a Test",
        "slug": "justatest",
        "levels": [[{"locale": "enUS", "translation": "foo"}]],
    }
    resp = await test_client.post(
        "/texts",
        json=payload,
    )
    assert resp.status_code == 201, status_fail_msg(201, resp)
    assert "id" in resp.json()
    assert "slug" in resp.json()
    assert resp.json()["slug"] == "justatest"
    # create duplicate
    resp = await test_client.post(
        "/texts",
        json=payload,
    )
    assert resp.status_code == 409, status_fail_msg(409, resp)


@pytest.mark.anyio
async def test_create_text_unauthorized(
    test_client: AsyncClient,
    status_fail_msg,
    login,
):
    await login()  # not a superuser (=unauthorized)!
    payload = {"title": "Meow", "slug": "meow", "levels": ["meow"]}
    resp = await test_client.post(
        "/texts",
        json=payload,
    )
    assert resp.status_code == 403, status_fail_msg(403, resp)


@pytest.mark.anyio
async def test_create_text_unauthenticated(
    test_client: AsyncClient,
    status_fail_msg,
):
    payload = {"title": "Meow", "slug": "meow", "levels": ["meow"]}
    resp = await test_client.post("/texts", json=payload)
    assert resp.status_code == 401, status_fail_msg(401, resp)


@pytest.mark.anyio
async def test_update_text(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
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

    # log in as superuser
    await login(is_superuser=True)

    # update text
    text_update = {"title": "Another text"}
    resp = await test_client.patch(
        f"/texts/{text['id']}",
        json=text_update,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert resp.json()["id"] == str(text["id"])
    assert "title" in resp.json()
    assert resp.json()["title"] == "Another text"

    # update unchanged text
    resp = await test_client.patch(
        f"/texts/{text['id']}",
        json=text_update,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # update invalid text
    text_update = {"title": "Yet another text"}
    resp = await test_client.patch(
        "/texts/637b9ad396d541a505e5439b",
        json=text_update,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_delete_text(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "nodes", "settings")
    text_id = inserted_ids["texts"][1]

    # log in as superuser
    await login(is_superuser=True)

    # try to delete text with wrong ID
    resp = await test_client.delete(
        f"/texts/{wrong_id}",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # delete text
    resp = await test_client.delete(
        f"/texts/{text_id}",
    )
    assert resp.status_code == 204, status_fail_msg(204, resp)

    # try to delete all texts (must fail because last text cannot be deleted)
    for text_id in inserted_ids["texts"]:
        resp = await test_client.delete(
            f"/texts/{text_id}",
        )
        delete_failed = resp.status_code == 400
        if delete_failed:
            break
    assert delete_failed


@pytest.mark.anyio
async def test_download_structure_template(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "nodes")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # download template
    resp = await test_client.get(
        f"/texts/{text_id}/template",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)

    # download template w/ wrong ID
    resp = await test_client.get(
        f"/texts/{wrong_id}/template",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)


@pytest.mark.anyio
async def test_insert_level(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    await insert_sample_data("texts", "nodes")

    # log in as superuser
    await login(is_superuser=True)

    # get text from db
    resp = await test_client.get("/texts")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) > 0
    text = resp.json()[0]
    assert len(text["levels"]) == 2

    # prepare new level data
    level_data = [
        {"locale": "enUS", "translation": "A level"},
        {"locale": "deDE", "translation": "Eine Ebene"},
    ]

    # insert new level 0
    resp = await test_client.post(
        f"/texts/{text['id']}/level/0",
        json=level_data,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert len(resp.json()["levels"]) == 3

    # insert new level 1
    resp = await test_client.post(
        f"/texts/{text['id']}/level/1",
        json=level_data,
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()
    assert len(resp.json()["levels"]) == 4

    # insert new level for wrong text ID
    resp = await test_client.post(
        f"/texts/{wrong_id}/level/0",
        json=level_data,
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # insert new level at invalid index
    resp = await test_client.post(
        f"/texts/{text['id']}/level/12",
        json=level_data,
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_delete_top_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    inserted_ids = await insert_sample_data("texts", "nodes")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # delete level 0
    resp = await test_client.delete(
        f"/texts/{text_id}/level/0",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_delete_bottom_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    inserted_ids = await insert_sample_data("texts", "nodes")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # delete level 1
    resp = await test_client.delete(
        f"/texts/{text_id}/level/1",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_delete_middle_level(
    test_client: AsyncClient,
    insert_sample_data,
    status_fail_msg,
    login,
):
    inserted_ids = await insert_sample_data("texts", "nodes")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # create extra level
    resp = await test_client.post(
        f"/texts/{text_id}/level/2",
        json=[{"locale": "*", "translation": "Some Level"}],
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()

    # delete level 1
    resp = await test_client.delete(
        f"/texts/{text_id}/level/1",
    )
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert "id" in resp.json()


@pytest.mark.anyio
async def test_fail_delete_level(
    test_client: AsyncClient, insert_sample_data, status_fail_msg, login, wrong_id
):
    inserted_ids = await insert_sample_data("texts", "nodes")
    text_id = inserted_ids["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # delete level for wrong text ID
    resp = await test_client.delete(
        f"/texts/{wrong_id}/level/0",
    )
    assert resp.status_code == 404, status_fail_msg(404, resp)

    # delete level at invalid index
    resp = await test_client.delete(
        f"/texts/{text_id}/level/12",
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)


@pytest.mark.anyio
async def test_import_text_structure(
    test_client: AsyncClient,
    insert_sample_data,
    get_sample_data_path,
    status_fail_msg,
    login,
    wrong_id,
):
    text_id = (await insert_sample_data("texts"))["texts"][0]

    # log in as superuser
    await login(is_superuser=True)

    # upload invalid structure definition file (give wrong MIME type)
    with open(get_sample_data_path("structure/fdhdgg.json"), "rb") as f:
        resp = await test_client.post(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "text/plain")},
        )
        assert resp.status_code == 400, status_fail_msg(400, resp)

    # upload invalid structure definition file (invalid JSON)
    resp = await test_client.post(
        f"/texts/{text_id}/structure",
        files={"file": ("fdhdgg.json", r"{foo: bar}", "application/json")},
    )
    assert resp.status_code == 400, status_fail_msg(400, resp)

    # upload structure definition file for wrong text ID
    with open(get_sample_data_path("structure/fdhdgg.json"), "rb") as f:
        resp = await test_client.post(
            f"/texts/{wrong_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert resp.status_code == 404, status_fail_msg(404, resp)

    # upload valid structure definition file
    with open(get_sample_data_path("structure/fdhdgg.json"), "rb") as f:
        resp = await test_client.post(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert resp.status_code == 201, status_fail_msg(201, resp)

    # try it again (should fail because text now already has nodes)
    with open(get_sample_data_path("structure/fdhdgg.json"), "rb") as f:
        resp = await test_client.post(
            f"/texts/{text_id}/structure",
            files={"file": (f.name, f, "application/json")},
        )
        assert resp.status_code == 409, status_fail_msg(409, resp)
