from tekst.db import Database


async def migration(db: Database) -> None:
    # rename field "custom_fonts" in "state" collection to "fonts"
    await db.state.update_many({}, {"$rename": {"custom_fonts": "fonts"}})
