from tekst.db import Database
from tekst.db.migrations import Migration


async def _proc(db: Database) -> None:
    # rename field "custom_fonts" in "state" collection to "fonts"
    await db.state.update_many({}, {"$rename": {"custom_fonts": "fonts"}})


MIGRATION = Migration(
    version="0.2.0a0",
    proc=_proc,
)
