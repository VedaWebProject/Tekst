from tekst.db import Database


async def migration(db: Database) -> None:
    await db.users.update_many(
        {},
        {"$push": {"user_notification_triggers": "removedFromOwners"}},
    )
