from datetime import UTC, datetime, timedelta
from os.path import realpath
from pathlib import Path

from beanie.odm.operators.find import BaseFindOperator
from beanie.operators import GTE, LT, Eq, In, Or
from bson import json_util
from deepdiff.diff import DeepDiff

from tekst import db, search
from tekst.auth import AccessTokenDocument, create_initial_superuser
from tekst.config import TekstConfig, get_config
from tekst.db import migrations
from tekst.logs import log, log_op_end, log_op_start
from tekst.models.common import PydanticObjectId
from tekst.models.content import ContentBaseDocument
from tekst.models.message import UserMessageDocument
from tekst.models.platform import PlatformStateDocument
from tekst.models.segment import (
    ClientSegmentDocument,
    ClientSegmentRead,
    ClientSegmentSignature,
)
from tekst.models.user import UserRead
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
    log.info("Cleanup: Deleting outdated access tokens...")
    await AccessTokenDocument.find(
        LT(
            AccessTokenDocument.created_at,
            datetime.now(UTC) - timedelta(seconds=cfg.security.access_token_lifetime),
        )
    ).delete()

    # delete stale user messages
    log.info("Cleanup: Deleting stale user messages...")
    await UserMessageDocument.find(
        LT(
            UserMessageDocument.created_at,
            datetime.now(UTC) - timedelta(days=cfg.misc.usrmsg_force_delete_after_days),
        ),
    ).delete()

    # delete adjacent content archive duplicates (keep oldest instance)
    log.info("Cleanup: Deleting adjacent content archive duplicates...")
    exclude_from_comparison = {
        "id",
        "_id",
        "resource_id",
        "location_id",
        "resource_type",
        "created_at",
        "archived",
    }
    async for content in ContentBaseDocument.find(
        Eq(ContentBaseDocument.archived, False),
        with_children=True,
    ):
        archived_versions = (
            await ContentBaseDocument.find(
                Eq(ContentBaseDocument.resource_id, content.resource_id),
                Eq(ContentBaseDocument.location_id, content.location_id),
                Eq(ContentBaseDocument.archived, True),
                with_children=True,
            )
            .sort(
                # oldest first!
                +ContentBaseDocument.created_at  # ty:ignore[unsupported-operator]
            )
            .to_list()
        )
        to_delete = []
        curr_v = None
        for v in archived_versions:
            if curr_v is None:
                curr_v = v
                continue
            if not DeepDiff(
                curr_v.model_dump(
                    exclude=exclude_from_comparison,
                    exclude_computed_fields=True,
                ),
                v.model_dump(
                    exclude=exclude_from_comparison,
                    exclude_computed_fields=True,
                ),
            ):
                to_delete.append(v)
            else:
                curr_v = v
        await ContentBaseDocument.find(
            In(ContentBaseDocument.id, [v.id for v in to_delete]),
            with_children=True,
        ).delete()

    return {"took": round(log_op_end(op_id), 2)}


async def _get_segment_restriction_queries(
    user: UserRead | None = None,
) -> tuple[BaseFindOperator] | tuple[dict]:
    if user is None:
        return (In(ClientSegmentDocument.restriction, ["none", None]),)
    if user.is_superuser:
        return ({},)
    return (In(ClientSegmentDocument.restriction, ["none", "user"]),)


async def get_segment(
    *,
    segment_id: PydanticObjectId | None = None,
    user: UserRead | None = None,
) -> ClientSegmentDocument | None:
    return await ClientSegmentDocument.find_one(
        Eq(ClientSegmentDocument.id, segment_id),
        *(await _get_segment_restriction_queries(user)),
    )


def _get_segments_query(system: bool | None = None) -> list[BaseFindOperator]:
    return (
        []
        if system is None
        else [
            GTE(ClientSegmentDocument.key, "system"),
            LT(ClientSegmentDocument.key, "systen"),
        ]
        if system
        else [
            Or(
                LT(ClientSegmentDocument.key, "system"),
                GTE(ClientSegmentDocument.key, "systen"),
            )
        ]
    )


async def get_segments_signatures(
    *,
    system: bool | None = None,
    user: UserRead | None = None,
) -> list[ClientSegmentSignature]:
    return (
        await ClientSegmentDocument.find(
            *_get_segments_query(system),
            *(await _get_segment_restriction_queries(user)),
        )
        .sort(+ClientSegmentDocument.sort_order)
        .project(ClientSegmentSignature)
        .to_list()
    )


async def get_segments(
    *,
    system: bool | None = None,
    user: UserRead | None = None,
) -> list[ClientSegmentRead]:
    return [
        ClientSegmentRead.model_from(segment)
        for segment in await ClientSegmentDocument.find(
            *_get_segments_query(system),
            *(await _get_segment_restriction_queries(user)),
        )
        .sort(+ClientSegmentDocument.sort_order)
        .to_list()
    ]
