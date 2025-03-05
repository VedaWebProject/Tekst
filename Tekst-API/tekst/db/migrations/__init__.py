import asyncio

from collections.abc import Callable
from importlib import import_module
from pkgutil import iter_modules

from packaging.version import Version

from tekst.db import Database, get_db
from tekst.logs import log


MigrationsDict = dict[str, Callable[[Database], None]]


def _sort_migrations(migrations: MigrationsDict) -> MigrationsDict:
    return {
        key: migrations[key] for key in sorted(migrations, key=lambda m: Version(m))
    }


def _read_migrations() -> MigrationsDict:
    return {
        mod.name.replace("migration_", "").replace("_", "."): import_module(
            f"{__name__}.{mod.name}"
        ).migration
        for mod in iter_modules(__path__)
    }


_MIGRATIONS = _read_migrations()


async def _is_migration_pending(db_version: str) -> bool:
    if db_version is None:
        log.warning("No DB version found. Has setup been run?")
        return False
    return bool(
        _MIGRATIONS and Version(db_version) < Version(list(_MIGRATIONS.keys())[-1])
    )


async def check_db_version(db_version: str, auto_migrate: bool = False) -> None:
    if await _is_migration_pending(db_version):
        if auto_migrate:
            log.warning("Found pending DB migrations.")
            await migrate()
        else:  # pragma: no cover
            # log a critical message and check again every minute for one hour to
            # give time to run the migrations in the background, then repeat
            log.critical(
                "Found pending DB migrations. "
                "The data in your database might not be compatible with "
                "the currently running version of Tekst. "
                "Please run the DB migrations now and keep this process running – "
                "it will check the DB again every minute for one hour and resume "
                "startup if migrations are complete."
            )
            for i in range(60):
                if await _is_migration_pending(db_version):
                    await asyncio.sleep(60)
                else:
                    break
            else:
                await check_db_version(db_version, auto_migrate=auto_migrate)


async def migrate() -> None:
    log.info("Running DB migrations...")

    db = get_db()
    if db is None:  # pragma: no cover
        log.error("DB client could not be initialized. Is MongoDB running?")
        return

    state_coll = db.get_collection("state")
    state = await state_coll.find_one()
    if state is None:
        log.error("No state document found. Has setup been run? Aborting migration.")
        return

    db_version_before: str | None = state.get("db_version")
    log.debug(f"DB version before migrations: {db_version_before}")

    if db_version_before is None:  # pragma: no cover
        log.error(
            "`db_version` not found in state document."
            "Has setup been run? Aborting migration."
        )
        return

    if not await _is_migration_pending(db_version_before):
        log.info("No DB migrations pending. Aborting migration.")
        return

    # run relevant migrations
    curr_db_version = db_version_before
    for migration_v in _MIGRATIONS:
        if Version(migration_v) > Version(curr_db_version):
            log.debug(f"Migrating DB from {curr_db_version} to {migration_v}...")
            try:
                await _MIGRATIONS[migration_v](db)
            except Exception as e:  # pragma: no cover
                log.error(
                    f"Failed migrating DB from {curr_db_version} "
                    f"to {migration_v}: {e}"
                )
                raise e
            curr_db_version = migration_v

    # update DB version in state document
    await state_coll.update_one(
        {"_id": state.get("_id")},
        {"$set": {"db_version": curr_db_version}},
    )
    log.info(f"Finished migrating DB from {db_version_before} to {curr_db_version}.")
