from tekst import db
from tekst.auth import create_initial_superuser
from tekst.config import TekstConfig, get_config
from tekst.logs import log
from tekst.resources import call_resource_maintenance_hooks, init_resource_types_mgr
from tekst.sample_data import insert_sample_data
from tekst.search import create_indices_task


async def app_setup():
    cfg: TekstConfig = get_config()
    log.info("Running Tekst pre-launch app setup...")
    init_resource_types_mgr()
    await db.init_odm()
    await insert_sample_data()
    await call_resource_maintenance_hooks()
    await create_initial_superuser()  # happens only when not in DEV mode
    if not cfg.dev_mode or cfg.dev.use_es:
        await create_indices_task()
    log.info("Finished Tekst pre-launch app setup.")
