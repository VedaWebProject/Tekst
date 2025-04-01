import asyncio

from collections.abc import Callable
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
        mig_name = mig_mod.name.replace("migration_", "").replace("_", ".")
        mig_fn = import_module(f"{__name__}.{mig_mod.name}").migration
        all_migrations[Version(mig_name)] = mig_fn
    return _sort_migrations(all_migrations)


def pending_migrations(db_version: str) -> MigrationsDict:
    all_migrations = _all_migrations()
    return {v: all_migrations[v] for v in all_migrations if v > Version(db_version)}


async def check_db_version(
    db_version: str,
    *,
    auto_migrate: bool = False,
    wait_for_migrations: bool = True,
) -> None:
    if db_version is None:  # pragma: no cover
        log.warning("No DB version found. Has setup been run?")
        return
    sys_ver = Version(tekst_meta["version"])
    db_ver = Version(db_version)
    pending = pending_migrations(db_version)
    latest_mig_ver = max(pending.keys()) if pending else Version(db_version)

    log.info("Checking system/DB compatibility...")
    log.debug(f"  Tekst version: {str(sys_ver)}")
    log.debug(f"  DB version: {str(db_ver)}")
    log.debug(f"  Latest migration version: {str(latest_mig_ver)}")
    log.debug(f"  Pending migrations: {', '.join([str(p) for p in pending]) or 'None'}")

    if len(pending):
        if auto_migrate:
            log.info("Found pending DB migrations.")
            await migrate()
        else:
            log.warning(
                "Found pending DB migrations. "
                "The data in your database might not be compatible with "
                "the currently running version of Tekst."
            )

        if not wait_for_migrations:  # pragma: no cover
            exit(1)
        else:  # pragma: no cover
            # log a critical message and check again every minute for one hour to
            # give time to run the migrations in the background, then repeat
            log.warning(
                "Please run the DB migrations now and keep this process running – "
                "it will check the DB again every minute for one hour and resume "
                "startup if migrations are complete."
            )
            for i in range(60):
                pending = pending_migrations(db_version)
                if len(pending):
                    await asyncio.sleep(60)
                else:
                    break
            else:
                await check_db_version(db_version, auto_migrate=auto_migrate)
    else:
        log.info("No pending DB migrations found.")


async def migrate() -> None:
    log.info("Running DB migrations...")

    db = get_db()
    if db is None:  # pragma: no cover
        log.critical("DB client could not be initialized. Is MongoDB running?")
        return

    state_coll = db.get_collection("state")
    state = await state_coll.find_one()
    if state is None:
        log.critical("No state document found. Has setup been run? Aborting migration.")
        return

    db_version_before: str | None = state.get("db_version")
    log.debug(f"DB version before migrations: {db_version_before}")

    if db_version_before is None:  # pragma: no cover
        log.critical(
            "`db_version` not found in state document."
            "Has setup been run? Aborting migration."
        )
        return

    pending = pending_migrations(db_version_before)
    if not len(pending):
        log.info("No pending DB migrations.")
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
    log.info(f"Finished migrating DB from {db_version_before} to {curr_db_version}.")
