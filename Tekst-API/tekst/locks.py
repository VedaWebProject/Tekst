from enum import Enum

from tekst.models.common import PlatformStateDocumentBase


class LockKey(Enum):
    INDEX_CREATE_UPDATE = "index_create_update"
    TEXT_STRUCTURE_IMPORT = "text_structure_import"


class LocksStatus(PlatformStateDocumentBase):
    index_create_update: bool = False
    text_structure_import: bool = False


async def _get_locks_doc() -> LocksStatus:
    return (
        await LocksStatus.find_one()
        or await LocksStatus.model_from(LocksStatus()).create()
    )


async def get_locks_status() -> dict[str, bool]:
    return (await _get_locks_doc()).model_dump(exclude={"id"})


async def is_locked(lock_key: LockKey) -> bool:
    locks = await _get_locks_doc()
    return getattr(locks, lock_key.value, False)


async def lock(lock_key: LockKey) -> None:
    locks = await _get_locks_doc()
    setattr(locks, lock_key.value, True)
    await locks.replace()


async def release(lock_key: LockKey) -> None:
    locks = await _get_locks_doc()
    setattr(locks, lock_key.value, False)
    await locks.replace()
