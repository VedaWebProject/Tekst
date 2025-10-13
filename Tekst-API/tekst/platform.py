from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from os.path import realpath
from pathlib import Path

from beanie.operators import GTE, LT, Eq, In, Or
from bson import json_util

from tekst import db, search
from tekst.auth import AccessTokenDocument, create_initial_superuser
from tekst.config import TekstConfig, get_config
from tekst.db import migrations
from tekst.logs import log, log_op_end, log_op_start
from tekst.models.common import PydanticObjectId
from tekst.models.message import UserMessageDocument
from tekst.models.platform import PlatformStateDocument
from tekst.models.segment import ClientSegmentDocument, ClientSegmentHead
from tekst.models.user import UserDocument
from tekst.resources import call_resource_precompute_hooks
from tekst.state import get_state, update_state


async def _insert_demo_data(cfg: TekstConfig = get_config()) -> bool:
    log.info("Inserting sample data...")
    database = db.get_db()
    target_collections = (
        "texts",
        "locations",
        "resources",
        "contents",
        "users",
        "state",
    )

    # check if any of the target collections contains data
    for collection in target_collections:
        if await database[collection].find_one():
            log.warning(
                f"Found data in collection: {collection}. "
                f"Skipping sample data insertion."
            )
            return False

    if cfg.dev_mode:
        # insert complete set of dev demo data
        for collection in target_collections:
            log.debug(f"Populating collection with sample data: {collection}...")
            path = cfg.misc.demo_data_path / f"{collection}.json"
            data = json_util.loads(path.read_text())
            result = await database[collection].insert_many(data)
            if not result.acknowledged:  # pragma: no cover
                log.error(f"Failed to insert dev data into collection: {collection}")
                raise RuntimeError("Failed to insert sample data.")
    else:
        # just insert the initial placeholder text
        path = Path(realpath(__file__)).parent / "welcome.json"
        data = json_util.loads(path.read_text())
        for collection in data:
            result = await database[collection].insert_many(data[collection])
            if not result.acknowledged:  # pragma: no cover
                log.error(f"Failed to insert data into collection: {collection}")
                raise RuntimeError("Failed to insert sample data.")

    return True


async def bootstrap(
    cfg: TekstConfig = get_config(),
    *,
    close_connections: bool = True,
):
    log.info("Running Tekst pre-launch bootstrap routine...")
    # init DB and ODM
    await db.init_odm()
    # insert demo data if DB collections are empty
    await _insert_demo_data(cfg)

    # check for pending migrations
    state: PlatformStateDocument = await get_state()
    if state.db_version:
        await migrations.check_for_migrations(
            db_version=state.db_version,
            auto_migrate=cfg.auto_migrate,
        )
    else:
        # set app version the DB data is based on in platform state
        state = await update_state(db_version=cfg.tekst["version"])

    # call resource precompute hooks (coverage, aggregations, ...)
    await call_resource_precompute_hooks()
    # create initial superuser (only when not in DEV mode)
    await create_initial_superuser(cfg)
    # create search indices (will skip up-to-date indices)
    await search.create_indices_task(cfg)

    if close_connections:  # pragma: no cover
        await db.close()
        await search.close()
    log.info("Finished Tekst pre-launch bootstrap routine.")


async def cleanup_task(cfg: TekstConfig = get_config()) -> dict[str, float]:
    op_id = log_op_start("Platform Cleanup", level="INFO")

    # delete outdated access tokens
    log.debug("Deleting outdated access tokens...")
    await AccessTokenDocument.find(
        LT(
            AccessTokenDocument.created_at,
            datetime.now(UTC) - timedelta(seconds=cfg.security.access_token_lifetime),
        )
    ).delete()

    # delete stale user messages
    log.debug("Deleting stale user messages...")
    await UserMessageDocument.find(
        LT(
            UserMessageDocument.created_at,
            datetime.now(UTC) - timedelta(days=cfg.misc.usrmsg_force_delete_after_days),
        ),
    ).delete()

    return {
        "took": round(log_op_end(op_id), 2),
    }


async def _get_segment_restriction_queries(
    user: UserDocument | None = None,
) -> tuple[Mapping]:
    if user is None:
        return (In(ClientSegmentDocument.restriction, ["none", None]),)
    if user.is_superuser:
        return tuple()
    return (In(ClientSegmentDocument.restriction, ["none", "user"]),)


async def get_segment(
    *,
    segment_id: PydanticObjectId | None = None,
    user: UserDocument | None = None,
) -> ClientSegmentDocument | None:
    return await ClientSegmentDocument.find_one(
        Eq(ClientSegmentDocument.id, segment_id),
        *(await _get_segment_restriction_queries(user)),
    )


async def get_segments(
    *,
    system: bool | None = None,
    user: UserDocument | None = None,
    head_projection: bool = False,
) -> list[ClientSegmentDocument]:
    system_segments_queries = (
        tuple()
        if system is None
        else (
            GTE(ClientSegmentDocument.key, "system"),
            LT(ClientSegmentDocument.key, "systen"),
        )
        if system
        else (
            Or(
                LT(ClientSegmentDocument.key, "system"),
                GTE(ClientSegmentDocument.key, "systen"),
            ),
        )
    )
    if not head_projection:
        return await ClientSegmentDocument.find(
            *system_segments_queries,
            *(await _get_segment_restriction_queries(user)),
        ).to_list()
    else:
        return (
            await ClientSegmentDocument.find(
                *system_segments_queries,
                *(await _get_segment_restriction_queries(user)),
            )
            .project(ClientSegmentHead)
            .to_list()
        )
