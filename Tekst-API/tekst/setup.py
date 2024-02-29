from tekst import db
from tekst.auth import create_initial_superuser
from tekst.config import TekstConfig
from tekst.logging import log, setup_logging
from tekst.resources import init_resource_types_mgr
from tekst.sample_data import insert_sample_data


async def app_setup(cfg: TekstConfig):
    setup_logging()
    log.info("Running Tekst pre-launch app setup...")
    init_resource_types_mgr()
    await db.init_odm()
    await insert_sample_data()
    await create_initial_superuser()  # happens only when not in DEV mode
    log.info("Finished Tekst pre-launch app setup.")
