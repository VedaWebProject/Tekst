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
    get_sample_data,
):
    data = get_sample_data("migrations/0_3_0a0.json")
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
    get_sample_data,
):
    res = get_sample_data("migrations/0_4_0a0.json")
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
async def test_0_4_1a0(database, get_sample_data):
    res = get_sample_data("migrations/0_4_1a0.json")
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
