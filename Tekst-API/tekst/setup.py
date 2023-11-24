from tekst.auth import create_initial_superuser, create_sample_users
from tekst.config import TekstConfig
from tekst.db import init_odm
from tekst.dependencies import get_db, get_db_client
from tekst.layer_types import init_layer_types_mgr
from tekst.logging import log, setup_logging
from tekst.sample_data import insert_sample_data


async def app_setup(cfg: TekstConfig):
    setup_logging()
    log.info("Running Tekst pre-launch app setup...")

    # log.info("Checking SMTP config...")
    # if not cfg.email_smtp_server:
    #     log.warning("No SMTP server configured")  # pragma: no cover

    init_layer_types_mgr()
    await init_odm(get_db(get_db_client(cfg), cfg))

    await create_sample_users()  # happens only when in DEV mode
    await insert_sample_data()  # doesn't happen during test runs
    await create_initial_superuser()  # happens only when not in DEV mode
    log.info("Finished Tekst pre-launch app setup.")
