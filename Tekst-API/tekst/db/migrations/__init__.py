from collections.abc import Callable
from datetime import UTC, datetime
from importlib import import_module
from pkgutil import iter_modules

from packaging.version import Version

from tekst import package_metadata as tekst_meta
from tekst.db import Database, get_db
from tekst.logs import log


MigrationsDict = dict[Version, Callable[[Database], None]]


def _sort_migrations(migrations: MigrationsDict) -> MigrationsDict:
    return {key: migrations[key] for key in sorted(migrations)}


def _all_migrations() -> MigrationsDict:
    all_migrations = dict()
    for mig_mod in iter_modules(__path__):
        if not mig_mod.name.startswith("migration_"):  # pragma: no cover
            continue
        mig_name = mig_mod.name.replace("migration_", "").replace("_", ".")
        mig_fn = import_module(f"{__name__}.{mig_mod.name}").migration
        all_migrations[Version(mig_name)] = mig_fn
    return _sort_migrations(all_migrations)


def pending_migrations(db_version: str) -> MigrationsDict:
    all_migrations = _all_migrations()
    return {v: all_migrations[v] for v in all_migrations if v > Version(db_version)}


async def check_for_migrations(
    db_version: str | None,
    *,
    auto_migrate: bool = False,
) -> None:
    if db_version is None:  # pragma: no cover
        log.critical("No DB version found. Has bootstrap routine been run?")
        exit(1)
    sys_ver = Version(tekst_meta["version"])
    db_ver = Version(db_version)
    pending = pending_migrations(db_version)
    latest_mig_ver = max(pending.keys()) if pending else Version(db_version)

    log.info("Checking system/DB compatibility...")
    log.debug(f"* Tekst version: {str(sys_ver)}")
    log.debug(f"* DB version: {str(db_ver)}")
    log.debug(f"* Latest migration version: {str(latest_mig_ver)}")
    log.debug(f"* Pending migrations: {', '.join([str(p) for p in pending]) or 'None'}")

    if not len(pending):
        log.info("No pending DB migrations found.")
        return

    if auto_migrate:
        log.info("Auto-migration is enabled. Running DB migrations now...")
        await migrate()
        return

    log.critical(
        "Found pending DB migrations. "
        "The data in your database might not be compatible with "
        "the currently running version of Tekst."
        "Please run the DB migrations before starting Tekst."
    )  # pragma: no cover
    exit(1)  # pragma: no cover


async def migrate() -> None:
    log.info("Running DB migrations...")

    db = get_db()
    if db is None:  # pragma: no cover
        log.critical(
            "DB client could not be initialized. Is MongoDB running? "
            "Is the DB connection properly configured? Aborting migration."
        )
        return

    state_coll = db.get_collection("state")
    state = await state_coll.find_one()
    if state is None:
        log.critical(
            "No state document found in DB. Has the bootstrap routine been run? "
            "Aborting migration."
        )
        return

    db_version_before: str | None = state.get("db_version")
    if not db_version_before:  # pragma: no cover
        log.critical(
            "db_version not found in state document."
            "Has bootstrap routine been run? Aborting migration."
        )
        return
    log.debug(f"DB version before migrations: {db_version_before}")

    # check for pending migrations
    pending = pending_migrations(db_version_before)
    if not len(pending):
        log.info("No pending DB migrations. Done.")
        return

    # run pending migrations
    curr_db_version = db_version_before
    for mig_ver in pending:
        log.info(f"Migrating DB from {curr_db_version} to {str(mig_ver)}...")
        try:
            await pending[mig_ver](db)
        except Exception as e:  # pragma: no cover
            log.error(
                f"Failed migrating DB from {curr_db_version} " f"to {str(mig_ver)}: {e}"
            )
            raise e
        curr_db_version = str(mig_ver)

    # update DB version in state document
    await state_coll.update_one(
        {"_id": state.get("_id")},
        {"$set": {"db_version": curr_db_version}},
    )

    # mark content as changed for all resources
    # to enforce complete regeneration of precomputed cache
    await db.resources.update_many(
        {},
        {"$set": {"contents_changed_at": datetime.now(UTC)}},
    )

    # mark search index as out-of-date for all texts to enforce regeneration
    await db.texts.update_many(
        {},
        {"$set": {"index_utd": False}},
    )

    log.info(f"Finished migrating DB from {db_version_before} to {curr_db_version}.")
