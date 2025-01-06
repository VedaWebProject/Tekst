from tekst.db import Database


async def migration(db: Database) -> None:
    """
    This migration procedre is a no-op since it belongs
    to the very first version handling migrations at all.
    """
