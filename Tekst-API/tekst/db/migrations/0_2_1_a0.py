from tekst.db import Database
from tekst.db.migrations import Migration


async def _proc(db: Database) -> None:
    # delete platform state field "register_intro_text"
    await db.state.update_many({}, {"$unset": {"register_intro_text": ""}})


MIGRATION = Migration(
    version="0.2.1a0",
    proc=_proc,
)
