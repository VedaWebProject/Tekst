import pytest

from tekst.db import migrations
from tekst.platform import bootstrap


@pytest.mark.anyio
async def test_bootstrap_tabula_rasa(config):
    # run app bootstrap – will insert sample data, run precomputation hooks, ...
    await bootstrap(close_connections=False)
    # 2nd time to test bootstrap attempt on already set-up instance DB
    await bootstrap(close_connections=False)


@pytest.mark.anyio
async def test_bootstrap_auto_migrate_no_pending(
    config,
    insert_test_data,
):
    await insert_test_data()  # need sample data, as an empty DB will not be migrated
    # run app bootstrap with auto_migrate == True (with no pending migrations)
    config.auto_migrate = True
    await bootstrap(config, close_connections=False)


@pytest.mark.anyio
async def test_bootstrap_auto_migrate_pending(
    config,
    database,
    insert_test_data,
):
    await insert_test_data()  # need sample data, as an empty DB will not be migrated
    # set bugus DB data version to 0.0.0
    await database["state"].update_one({}, {"$set": {"db_version": "0.0.0"}})
    # run app bootstrap with auto_migrate == True (with no pending migrations)
    config.auto_migrate = True
    await bootstrap(config, close_connections=False)


@pytest.mark.anyio
async def test_migrate_no_state_coll(
    database,
    insert_test_data,
):
    await insert_test_data()  # need sample data, as an empty DB will not be migrated
    # drop state collection to test failing migration with missing state
    await database.drop_collection("state")
    await migrations.migrate()


@pytest.mark.anyio
async def test_migrate_none_pending(
    config,
):
    await bootstrap(close_connections=False)
    await migrations.migrate()  # no pending migrations


@pytest.mark.anyio
async def test_prod_startup(
    config,
    database,
):
    # clone config object
    prod_cfg = config.model_copy(deep=True)
    prod_cfg.dev_mode = False
    await bootstrap(prod_cfg, close_connections=False)
    assert await database.texts.count_documents({}) == 1
    assert await database.locations.count_documents({}) == 1
    assert await database.resources.count_documents({}) == 1
    assert await database.contents.count_documents({}) == 1
