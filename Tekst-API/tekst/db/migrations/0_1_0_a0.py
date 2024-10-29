from tekst.db import Database
from tekst.db.migrations import Migration


async def _proc(db: Database) -> None:
    """
    This migration procedre is a no-op since it belongs
    to the very first version handling migrations at all.
    """


MIGRATION = Migration(
    version="0.1.0a0",
    proc=_proc,
)
