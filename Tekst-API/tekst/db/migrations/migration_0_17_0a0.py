from tekst.db import Database


async def migration(db: Database) -> None:
    await db.texts.update_many({}, {"$unset": {"pinned_metadata_ids": ""}})
