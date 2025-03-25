from tekst.db import Database


async def migration(db: Database) -> None:
    # rename field "description" in all resources to "subtitle"
    await db.resources.update_many(
        {},
        {"$rename": {"description": ("subtitle")}},
    )
    # rename field "comment" in all resources to "description"
    await db.resources.update_many(
        {},
        {"$rename": {"comment": "description"}},
    )
