import pytest

from tekst.db import migrations
from tekst.setup import app_setup


@pytest.mark.anyio
async def test_setup_tabula_rasa(config):
    await app_setup()
    await app_setup()  # 2nd time to test setup attempt on already set-up instance DB


@pytest.mark.anyio
async def test_setup_auto_migrate_no_pending(
    config,
    insert_sample_data,
):
    await insert_sample_data()  # need sample data, as an empty DB will not be migrated
    # run app setup with auto_migrate == True (with no pending migrations)
    config.auto_migrate = True
    await app_setup(config)


@pytest.mark.anyio
async def test_setup_auto_migrate_pending(
    config,
    get_db_client_override,
    insert_sample_data,
):
    await insert_sample_data()  # need sample data, as an empty DB will not be migrated
    database = get_db_client_override[config.db.name]
    # set bugus DB data version to 0.0.0
    await database["state"].update_one({}, {"$set": {"db_version": "0.0.0"}})
    # run app setup with auto_migrate == True (with no pending migrations)
    config.auto_migrate = True
    await app_setup(config)


@pytest.mark.anyio
async def test_migrate_no_state_coll(
    config,
    get_db_client_override,
    insert_sample_data,
):
    await insert_sample_data()  # need sample data, as an empty DB will not be migrated
    database = get_db_client_override[config.db.name]
    # drop state collection to test failing migration with missing state
    await database.drop_collection("state")
    await migrations.migrate()


@pytest.mark.anyio
async def test_migrate_none_pending(
    config,
    insert_sample_data,
):
    await app_setup()
    await migrations.migrate()  # no pending migrations
