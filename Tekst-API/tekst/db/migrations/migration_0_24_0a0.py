from tekst.db import Database


async def migration(db: Database) -> None:
    await db.texts.update_many(
        {},
        {"$rename": {"accent_color": "color"}},
    )
