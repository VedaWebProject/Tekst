from tekst.db import Database


async def migration(db: Database) -> None:
    # move plain text-specific config in to config sub-document
    await db.resources.update_many(
        {"resource_type": "plainText"},
        {"$set": {"config.plainText": {}}},
    )
    await db.resources.update_many(
        {"resource_type": "plainText"},
        {
            "$rename": {
                "config.deeplLinks": "config.plainText.deeplLinks",
                "config.lineLabelling": "config.plainText.lineLabelling",
            }
        },
    )
    # move text annotation-specific config in to config sub-document
    await db.resources.update_many(
        {"resource_type": "textAnnotation"},
        {"$set": {"config.textAnnotation": {}}},
    )
    await db.resources.update_many(
        {"resource_type": "textAnnotation"},
        {
            "$rename": {
                "config.annotationGroups": "config.textAnnotation.annotationGroups",
                "config.displayTemplate": "config.textAnnotation.displayTemplate",
                "config.multiValueDelimiter": (
                    "config.textAnnotation.multiValueDelimiter"
                ),
            }
        },
    )
