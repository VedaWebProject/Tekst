from humps import decamelize

from tekst.db import Database


async def migration(db: Database) -> None:
    # for all resources, move config items "config.general.default_collapsed"
    # and "config.general.font" to "config.common"
    await db.resources.update_many(
        {},
        {
            "$rename": {
                "config.general.default_collapsed": "config.common.default_collapsed",
                "config.general.font": "config.common.font",
            },
        },
    )

    # for each resource, move remaining config items from
    # "config.general" to "config.special"
    resources = await db.resources.find().to_list()
    for res in resources:
        await db.resources.update_one(
            {"_id": res["_id"]},
            {
                "$rename": {
                    f"config.general.{general_cfg_field}": (
                        f"config.special.{general_cfg_field}"
                    )
                    for general_cfg_field in res["config"]["general"]
                },
            },
        )

    # for all resources, remove field "config.general"
    await db.resources.update_many(
        {},
        {
            "$unset": {
                "config.general": "",
            },
        },
    )

    # for all resources, rename "config.common" to "config.general"
    await db.resources.update_many(
        {},
        {"$rename": {"config.common": "config.general"}},
    )

    # for textAnnotation-type resources:
    # - move annotation-specific config items into "config.special.annotations"
    await db.resources.update_many(
        {"resource_type": "textAnnotation"},
        {
            "$rename": {
                "config.text_annotation.annotation_groups": (
                    "config.special.annotations.groups"
                ),
                "config.text_annotation.display_template": (
                    "config.special.annotations.display_template"
                ),
                "config.text_annotation.multi_value_delimiter": (
                    "config.special.annotations.multi_value_delimiter"
                ),
            }
        },
    )

    # for "locationMetadata"-type resources:
    # - move key-value item display config items into "config.special.item_display"
    await db.resources.update_many(
        {"resource_type": "locationMetadata"},
        {
            "$rename": {
                "config.location_metadata.groups": "config.special.item_display.groups",
                "config.location_metadata.display_props": (
                    "config.special.item_display.display_props"
                ),
            }
        },
    )

    # for "apiCall"-type resources:
    # - move api call-specific config items into "config.special.api_call"
    # - move response transformation-specific config items into
    #   "config.special.transform"
    await db.resources.update_many(
        {"resource_type": "apiCall"},
        {
            "$rename": {
                "config.api_call.endpoint": "config.special.api_call.endpoint",
                "config.api_call.method": "config.special.api_call.method",
                "config.api_call.content_type": "config.special.api_call.content_type",
                "config.api_call.transform_deps": "config.special.transform.deps",
                "config.api_call.transform_js": "config.special.transform.js",
            }
        },
    )

    # for each resource, move remaining config items from
    # "config.<resource_type>" to "config.special"
    resources = await db.resources.find().to_list()
    for res in resources:
        res_type_snake = decamelize(res["resource_type"])
        await db.resources.update_one(
            {"_id": res["_id"]},
            {
                "$rename": {
                    f"config.{res_type_snake}.{special_cfg_field}": (
                        f"config.special.{special_cfg_field}"
                    )
                    for special_cfg_field in res["config"].get(res_type_snake, {})
                },
            },
        )

    # for each resource, remove field "config.<resource_type>"
    resources = await db.resources.find().to_list()
    for res in resources:
        res_type_snake = decamelize(res["resource_type"])
        await db.resources.update_one(
            {"_id": res["_id"]},
            {
                "$unset": {
                    f"config.{res_type_snake}": "",
                },
            },
        )
