from tekst.db import Database


async def migration(db: Database) -> None:
    await db.resources.update_many(
        {},
        {"$rename": {"original_id": "patch_for"}},
    )
