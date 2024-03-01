from enum import Enum

from humps import dekebabize

from tekst.models.common import PlatformStateDocumentBase


class LockKey(Enum):
    INDEX_CREATE_UPDATE = "index-create-update"
    TEXT_STRUCTURE_IMPORT = "text-structure-import"


class LocksStatus(PlatformStateDocumentBase):
    index_create_update: bool = False
    text_structure_import: bool = False


async def _get_locks() -> LocksStatus:
    return (
        await LocksStatus.find_one()
        or await LocksStatus.model_from(LocksStatus()).create()
    )


async def is_locked(lock_key: LockKey) -> bool:
    locks = await _get_locks()
    return getattr(locks, dekebabize(lock_key.value), False)


async def lock(lock_key: LockKey) -> None:
    locks = await _get_locks()
    setattr(locks, dekebabize(lock_key.value), True)
    await locks.replace()


async def unlock(lock_key: LockKey) -> None:
    locks = await _get_locks()
    setattr(locks, dekebabize(lock_key.value), False)
    await locks.replace()
