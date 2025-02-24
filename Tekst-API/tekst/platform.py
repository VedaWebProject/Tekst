from datetime import datetime, timedelta

from beanie.operators import LT

from tekst import db
from tekst.auth import AccessTokenDocument, create_initial_superuser
from tekst.config import TekstConfig, get_config
from tekst.db import migrations
from tekst.logs import log, log_op_end, log_op_start
from tekst.models.message import UserMessageDocument
from tekst.models.platform import PlatformStateDocument
from tekst.resources import call_resource_precompute_hooks, init_resource_types_mgr
from tekst.sample_data import insert_sample_data
from tekst.search import create_indices_task
from tekst.state import get_state, update_state


async def app_setup(cfg: TekstConfig = get_config()):
    log.info("Running Tekst pre-launch app setup...")

    # register all resource types
    init_resource_types_mgr()

    # init DB and ODM
    await db.init_odm()

    # insert sample data if DB collections are empty
    inserted_sample_data: bool = await insert_sample_data()

    # check for pending migrations
    state: PlatformStateDocument = await get_state()
    if state.db_version and not inserted_sample_data:
        await migrations.check_db_version(
            db_version=state.db_version,
            auto_migrate=cfg.auto_migrate,
        )
    else:
        # set app version the DB data is based on in platform state
        state = await update_state(db_version=cfg.tekst["version"])

    # call resource precompute hooks (coverage, aggregations, ...)
    await call_resource_precompute_hooks()

    # create initial superuser (only when not in DEV mode)
    await create_initial_superuser()

    # create search indices (will skip up-to-date indices)
    if not cfg.dev_mode or cfg.dev.use_es:
        await create_indices_task()

    log.info("Finished Tekst pre-launch app setup.")


async def cleanup_task(cfg: TekstConfig = get_config()) -> dict[str, float]:
    op_id = log_op_start("Platform Cleanup", level="INFO")

    # delete outdated access tokens
    log.debug("Deleting outdated access tokens...")
    await AccessTokenDocument.find(
        LT(
            AccessTokenDocument.created_at,
            datetime.utcnow() - timedelta(seconds=cfg.security.access_token_lifetime),
        )
    ).delete()

    # delete stale user messages
    log.debug("Deleting stale user messages...")
    await UserMessageDocument.find(
        LT(
            UserMessageDocument.created_at,
            datetime.utcnow() - timedelta(days=cfg.misc.usrmsg_force_delete_after_days),
        ),
    ).delete()

    return {
        "took": round(log_op_end(op_id), 2),
    }
