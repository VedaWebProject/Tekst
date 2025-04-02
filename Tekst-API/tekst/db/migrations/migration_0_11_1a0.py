from tekst.db import Database


async def migration(db: Database) -> None:
    # rename field "default_collapsed" in general config to "collapsible_contents"
    await db.resources.update_many(
        {},
        {
            "$rename": {
                "config.general.default_collapsed": (
                    "config.general.collapsible_contents"
                )
            }
        },
    )

    # remove "collapsible_contents" where it is explicitly set to False
    await db.resources.update_many(
        {"config.general.collapsible_contents": False},
        {"$unset": {"config.general.collapsible_contents": ""}},
    )

    # change value for "collapsible_contents" from True to 400 (pixels)
    await db.resources.update_many(
        {"config.general.collapsible_contents": True},
        {"$set": {"config.general.collapsible_contents": 400}},
    )
