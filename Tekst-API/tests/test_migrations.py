import pytest

from bson import ObjectId
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
    insert_sample_data,
    wrong_id,
):
    resource_id = (await insert_sample_data())["resources"][0]
    await database.corrections.insert_one(
        {
            "resource_id": ObjectId(resource_id),
            "note": "foo",
            "user_id": ObjectId(wrong_id),
            "position": 0,
        }
    )
    await migrations.migration_0_3_0a0.migration(database)
    correction = await database.corrections.find_one({})
    assert correction
    assert "location_id" in correction
