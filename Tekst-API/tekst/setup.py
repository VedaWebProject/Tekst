from tekst import db
from tekst.auth import create_initial_superuser
from tekst.config import TekstConfig, get_config
from tekst.logging import log, setup_logging
from tekst.resources import init_resource_types_mgr
from tekst.sample_data import insert_sample_data
from tekst.search import setup_elasticsearch, task_create_index


async def app_setup():
    cfg: TekstConfig = get_config()
    setup_logging()
    log.info("Running Tekst pre-launch app setup...")
    init_resource_types_mgr()
    await db.init_odm()
    await insert_sample_data()
    await create_initial_superuser()  # happens only when not in DEV mode
    if not cfg.dev_mode or cfg.dev_use_es:
        await setup_elasticsearch()
        await task_create_index()
    log.info("Finished Tekst pre-launch app setup.")
