from tekst.db import Database


async def migration(db: Database) -> None:
    # rename field "reduced_view" in plain text general config to "focus_view"
    await db.resources.update_many(
        {"resource_type": "plainText"},
        {"$rename": {"config.general.reduced_view": ("config.general.focus_view")}},
    )
    # rename field "single_line_delimiter" in focus view config to "delimiter"
    await db.resources.update_many(
        {"resource_type": "plainText"},
        {
            "$rename": {
                "config.general.focus_view.single_line_delimiter": (
                    "config.general.focus_view.delimiter"
                )
            }
        },
    )
