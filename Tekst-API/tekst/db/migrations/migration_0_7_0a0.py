from tekst.db import Database


async def migration(db: Database) -> None:
    # rename "time" field in UserMessage documents to "created_at"
    await db.messages.update_many({}, {"$rename": {"time": "created_at"}})
