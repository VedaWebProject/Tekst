import pytest

from tekst.db import migrations


@pytest.mark.anyio
async def test_0_1_0a0(database):
    await migrations.migration_0_1_0a0.migration(database)  # no-op


@pytest.mark.anyio
async def test_0_2_0a0(database):
    await database.state.insert_one({"custom_fonts": ["foo", "bar"]})
    await migrations.migration_0_2_0a0.migration(database)
    state = await database.state.find_one({})
    assert "fonts" in state
    assert "custom_fonts" not in state
    assert state.get("fonts")[1] == "bar"


@pytest.mark.anyio
async def test_0_2_1a0(database):
    await database.state.insert_one({"register_intro_text": ["foo", "bar"]})
    await migrations.migration_0_2_1a0.migration(database)
    state = await database.state.find_one({})
    assert "register_intro_text" not in state
    assert len(state.keys()) == 1
    assert "_id" in state


@pytest.mark.anyio
async def test_0_3_0a0(
    database,
    get_test_data,
):
    data = get_test_data("migrations/0_3_0a0.json")
    for coll_name in data:
        await database[coll_name].insert_many(data[coll_name])

    # run migration
    await migrations.migration_0_3_0a0.migration(database)

    # assert the data has been fixed by the migration
    correction = await database.corrections.find_one({})
    assert correction
    assert "location_id" in correction
    assert str(correction["location_id"]) == "654b825533ee5737b297f8e5"
    assert not await database.precomputed.find_one({"precomputed_type": "coverage"})


@pytest.mark.anyio
async def test_0_4_0a0(
    database,
    get_test_data,
):
    res = get_test_data("migrations/0_4_0a0.json")
    res_id = (await database.resources.insert_one(res)).inserted_id
    assert res_id

    # run migration
    await migrations.migration_0_4_0a0.migration(database)
    res = await database.resources.find_one({"_id": res_id})

    # assert the data has been fixed by the migration
    assert "config" in res
    assert "deeplLinks" not in res["config"]
    assert "plainText" in res["config"]
    assert "deeplLinks" in res["config"]["plainText"]


@pytest.mark.anyio
async def test_0_4_1a0(database, get_test_data):
    res = get_test_data("migrations/0_4_1a0.json")
    res_id = (await database.resources.insert_one(res)).inserted_id
    assert res_id

    # run migration
    await migrations.migration_0_4_1a0.migration(database)
    res = await database.resources.find_one({"_id": res_id})

    # assert the data has been fixed by the migration
    assert "config" in res
    assert "plainText" not in res["config"]
    assert "plain_text" in res["config"]
    assert "deepl_links" in res["config"]["plain_text"]
    assert "source_language" in res["config"]["plain_text"]["deepl_links"]


@pytest.mark.anyio
async def test_0_4_2a0(database, get_test_data):
    content = get_test_data("migrations/0_4_2a0.json")
    content_id = (await database.contents.insert_one(content)).inserted_id
    assert content_id

    # run migration
    await migrations.migration_0_4_2a0.migration(database)
    content = await database.contents.find_one({"_id": content_id})

    # assert the data has been fixed by the migration
    assert "extra" not in content
    assert "transform_context" in content


@pytest.mark.anyio
async def test_0_5_0a0(database, get_test_data):
    res = get_test_data("migrations/0_5_0a0.json")
    conf_val = res["config"]["common"]["show_on_parent_level"]
    assert conf_val is not None
    res_id = (await database.resources.insert_one(res)).inserted_id
    assert res_id

    # run migration
    await migrations.migration_0_5_0a0.migration(database)
    res = await database.resources.find_one({"_id": res_id})

    # assert the data has been fixed by the migration
    assert "config" in res
    assert "common" in res["config"]
    assert "show_on_parent_level" not in res["config"]["common"]
    assert "enable_content_context" in res["config"]["common"]
    assert res["config"]["common"]["enable_content_context"] == conf_val


@pytest.mark.anyio
async def test_0_6_0a0(database, get_test_data):
    state = get_test_data("migrations/0_6_0a0.json")
    await database.state.insert_one(state)

    # run migration
    await migrations.migration_0_6_0a0.migration(database)
    state = await database.state.find_one({})

    # assert the data has been fixed by the migration
    assert "always_show_text_info" not in state


@pytest.mark.anyio
async def test_0_7_0a0(database, get_test_data):
    msg = get_test_data("migrations/0_7_0a0.json")
    await database.messages.insert_one(msg)

    # run migration
    await migrations.migration_0_7_0a0.migration(database)
    msg = await database.messages.find_one({})

    # assert the data has been fixed by the migration
    assert "time" not in msg
    assert "created_at" in msg


@pytest.mark.anyio
async def test_0_8_0a0(database, get_test_data):
    footer_segment = get_test_data("migrations/0_8_0a0.json")
    await database.segments.insert_one(footer_segment)

    # run migration
    await migrations.migration_0_8_0a0.migration(database)
    footer_segment = await database.segments.find_one({})

    # assert the data has been fixed by the migration
    assert "key" in footer_segment
    assert footer_segment["key"] == "systemFooterUpper"


@pytest.mark.anyio
async def test_0_9_0a0(
    database,
    get_test_data,
):
    resources = get_test_data("migrations/0_9_0a0.json")
    await database.resources.insert_many(resources)

    # run migration
    await migrations.migration_0_9_0a0.migration(database)
    resources = await database.resources.find({"resource_type": "plainText"}).to_list()

    # assert the data has been fixed by the migration
    assert len(resources) > 0
    for res in resources:
        assert "reduced_view" not in res["config"]["general"]
        assert "focus_view" in res["config"]["general"]
        assert "single_line" in res["config"]["general"]["focus_view"]
        assert "single_line_delimiter" not in res["config"]["general"]["focus_view"]
        assert "delimiter" in res["config"]["general"]["focus_view"]
