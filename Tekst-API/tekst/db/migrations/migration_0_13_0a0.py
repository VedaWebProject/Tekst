from tekst.db import Database


async def migration(db: Database) -> None:
    await db.contents.update_many(
        {},
        {
            "$rename": {
                "comment": "authors_comment",
                "notes": "editors_comment",
            }
        },
    )
