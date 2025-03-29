from humps import decamelize

from tekst.db import Database


async def migration(db: Database) -> None:
    # for each resource, move config items from "config.general" and
    # "config.<resource_type>" to "config.special"
    # also, remove "config.general" and "config.<resource_type>"
    resources = await db.resources.find().to_list()
    for res in resources:
        rtype_snake = decamelize(res["resource_type"])
        await db.resources.update_one(
            {"_id": res["_id"]},
            {
                "$set": {
                    "config.special": dict(
                        **res["config"]["general"],
                        **res["config"].get(rtype_snake, {}),
                    )
                },
                "$unset": {
                    "config.general": "",
                    f"config.{rtype_snake}": "",
                },
            },
        )

    # for each resource, rename "config.common" to "config.general"
    await db.resources.update_many(
        {},
        {"$rename": {"config.common": "config.general"}},
    )

    # for each resource, move "config.special.default_collapsed"
    # to "config.general.default_collapsed"
    await db.resources.update_many(
        {},
        {
            "$rename": {
                "config.special.default_collapsed": "config.general.default_collapsed"
            }
        },
    )

    # for each resource, move "config.special.font" to "config.general.font"
    await db.resources.update_many(
        {},
        {"$rename": {"config.special.font": "config.general.font"}},
    )
