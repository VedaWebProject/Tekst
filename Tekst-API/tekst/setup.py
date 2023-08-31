from tekst.auth import create_initial_superuser, create_sample_users
from tekst.config import TekstConfig
from tekst.db import init_odm
from tekst.dependencies import get_db, get_db_client
from tekst.layer_types import init_layer_type_manager
from tekst.logging import log, setup_logging
from tekst.models.settings import PlatformSettingsDocument
from tekst.sample_data import create_sample_texts


async def app_setup(cfg: TekstConfig):
    setup_logging()
    log.info("Running Tekst pre-launch app setup...")

    log.info("Checking SMTP config...")
    if not cfg.email_smtp_server:
        log.critical("No SMTP server configured. Aborting setup...")
        exit(1)

    init_layer_type_manager()
    await init_odm(get_db(get_db_client(cfg), cfg))

    log.info("Creating initial platform settings from defaults...")
    if not (await PlatformSettingsDocument.find_one().exists()):
        await PlatformSettingsDocument().create()
    else:
        log.warning("Platform settings already exist. Skipping settings creation.")

    await create_sample_users()
    await create_sample_texts()
    await create_initial_superuser()
