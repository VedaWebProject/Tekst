from tekst.db import Database


async def migration(db: Database) -> None:
    # rename field "extra" in API Call content documents "transform_context"
    await db.contents.update_many(
        {"resource_type": "apiCall"}, {"$rename": {"extra": "transform_context"}}
    )
