from tekst.db import Database


async def migration(db: Database) -> None:
    # rename field "show_on_parent_level" in common
    # resource config to "enable_content_context"
    await db.resources.update_many(
        {},
        {
            "$rename": {
                "config.common.show_on_parent_level": (
                    "config.common.enable_content_context"
                )
            }
        },
    )
