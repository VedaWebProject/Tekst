from datetime import UTC, datetime

from tekst.db import Database


async def migration(db: Database) -> None:
    await db.contents.update_many(
        {},
        {
            "$set": {
                "created_at": datetime.min.replace(tzinfo=UTC),  # earliest possible
                "archived": False,
            }
        },
    )
