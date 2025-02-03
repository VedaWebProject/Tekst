from tekst.db import Database


async def migration(db: Database) -> None:
    # move plain text-specific config in to config sub-document
    await db.resources.update_many(
        {"resource_type": "plainText"},
        {
            "$rename": {
                "config.deepl_links": "config.plain_text.deepl_links",
                "config.line_labelling": "config.plain_text.line_labelling",
            }
        },
    )
    # move text annotation-specific config in to config sub-document
    await db.resources.update_many(
        {"resource_type": "textAnnotation"},
        {
            "$rename": {
                "config.annotation_groups": "config.text_annotation.annotation_groups",
                "config.display_template": "config.text_annotation.display_template",
                "config.multi_value_delimiter": (
                    "config.text_annotation.multi_value_delimiter"
                ),
            }
        },
    )
