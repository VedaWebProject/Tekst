from tekst import db
from tekst.auth import create_initial_superuser
from tekst.config import TekstConfig, get_config
from tekst.db import migrations
from tekst.logs import log
from tekst.models.platform import PlatformStateDocument
from tekst.resources import call_resource_maintenance_hooks, init_resource_types_mgr
from tekst.sample_data import insert_sample_data
from tekst.search import create_indices_task
from tekst.state import get_state, update_state


async def app_setup():
    log.info("Running Tekst pre-launch app setup...")

    # register all resource types
    init_resource_types_mgr()

    # init DB and ODM
    await db.init_odm()

    cfg: TekstConfig = get_config()
    state: PlatformStateDocument = await get_state()

    # insert sample data if DB collections are empty
    inserted_sample_data: bool = await insert_sample_data()

    # check for pending migrations
    if state.db_version and not inserted_sample_data:
        await migrations.check_db_version(state.db_version)
    else:
        # set app version the DB data is based on in platform state
        state = await update_state(db_version=cfg.tekst["version"])

    # call resource maintenance hooks (precompute aggregations and such)
    await call_resource_maintenance_hooks()

    # create initial superuser (only when not in DEV mode)
    await create_initial_superuser()

    # create search indices (will skip up-to-date indices)
    if not cfg.dev_mode or cfg.dev.use_es:
        await create_indices_task()

    log.info("Finished Tekst pre-launch app setup.")
