from tekst.db import Database


async def migration(db: Database) -> None:
    # rename system segment key "systemFooter" to "systemFooterUpper"
    await db.segments.update_many(
        {"key": "systemFooter"}, {"$set": {"key": "systemFooterUpper"}}
    )
