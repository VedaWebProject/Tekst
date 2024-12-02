import pytest

from tekst.db import migrations
from tekst.setup import app_setup


@pytest.mark.anyio
async def test_setup(config):
    await app_setup()
    await app_setup()  # 2nd time to test setup attempt on already set-up instance DB
    # run app setup with auto_migrate == True (with no pending migrations)
    config.auto_migrate = True
    await app_setup(config)


@pytest.mark.anyio
async def test_db_migrations(
    config,
    get_db_client_override,
    insert_sample_data,
):
    # run migrations without prior DB setup
    await migrations.migrate()
    await insert_sample_data()
    database = get_db_client_override[config.db.name]
    # set bugus DB data version to 0.0.0
    await database["state"].update_one({}, {"$set": {"db_version": "0.0.0"}})
    # run migrations with properly set-up DB
    await migrations.migrate()
