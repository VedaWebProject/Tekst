from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from pkgutil import iter_modules

from packaging.version import Version

from tekst.db import Database, get_db
from tekst.logs import log


@dataclass
class Migration:
    version: str
    proc: Callable[[Database], None]


def _sort_migrations(migrs: list[Migration]) -> list[Migration]:
    return sorted(migrs, key=lambda m: Version(m.version))


def _list_migrations() -> list[Migration]:
    return _sort_migrations(
        [
            import_module(f"{__name__}.{mod.name}").MIGRATION
            for mod in iter_modules(__path__)
        ]
    )


_MIGRATIONS = _list_migrations()


async def _is_migration_pending(db_version: str) -> bool:
    if db_version is None:
        log.error("No DB version found. Has setup been run?")
        return
    return bool(_MIGRATIONS and Version(db_version) < Version(_MIGRATIONS[-1].version))


async def check_db_version(db_version: str, exit_on_fail: bool = True) -> None:
    if await _is_migration_pending(db_version):
        log.critical(
            "Found pending DB migrations. "
            "The data in your database might not be compatible with "
            "the currently running version of Tekst. Please run the DB migrations!"
        )
        if exit_on_fail:
            exit(1)


async def migrate() -> None:
    log.info("Running DB migrations...")

    db = get_db()
    if db is None:
        log.error("DB client could not be initialized. Is MongoDB running?")
        return

    state_coll = db.get_collection("state")
    if state_coll is None:
        log.error(
            "DB collection 'state' not found. Has setup been run? Aborting migration."
        )
        return

    state = await state_coll.find_one()
    if state is None:
        log.error("No state document found. Has setup been run? Aborting migration.")
        return

    db_version_before: str | None = state.get("db_version")
    log.debug(f"DB version before migrations: {db_version_before}")

    if db_version_before is None:
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
    for migration in _MIGRATIONS:
        if Version(migration.version) > Version(curr_db_version):
            log.debug(f"Migrating DB from {curr_db_version} to {migration.version}...")
            try:
                await migration.proc(db)
            except Exception as e:
                log.error(
                    f"Failed migrating DB from {curr_db_version} "
                    f"to {migration.version}: {e}"
                )
                raise e
            curr_db_version = migration.version

    # update DB version in state document
    await state_coll.update_one(
        {"_id": state.get("_id")},
        {"$set": {"db_version": curr_db_version}},
    )
    log.info(f"Finished migrating DB from {db_version_before} to {curr_db_version}.")
