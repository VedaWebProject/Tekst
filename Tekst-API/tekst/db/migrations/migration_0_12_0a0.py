from tekst.db import Database
from tekst.logs import log


async def migration(db: Database) -> None:
    # rename "locationMetadata" resources'
    # "config.special.item_display" to
    # "config.special.entries_integration"
    await db.resources.update_many(
        {"resource_type": "locationMetadata"},
        {
            "$rename": {
                "config.special.item_display": "config.special.entries_integration"
            }
        },
    )

    # rename "locationMetadata" resources'
    # "config.special.entries_integration.display_props" to
    # "config.special.entries_integration.item_props"
    await db.resources.update_many(
        {"resource_type": "locationMetadata"},
        {
            "$rename": {
                "config.special.entries_integration.display_props": (
                    "config.special.entries_integration.item_props"
                )
            }
        },
    )

    # rename "locationMetadata" resources'
    # "config.special.entries_integration.groups[n].name" to
    # "config.special.entries_integration.groups[n].key"
    for res in await db.resources.find({"resource_type": "locationMetadata"}).to_list():
        try:
            for group in res["config"]["special"]["entries_integration"]["groups"]:
                if "name" not in group:
                    continue
                group["key"] = group["name"]
                del group["name"]
            await db.resources.update_one(
                {"_id": res["_id"]},
                {
                    "$set": {
                        "config.special.entries_integration.groups": res["config"][
                            "special"
                        ]["entries_integration"]["groups"]
                    }
                },
            )
        except Exception as e:  # pragma: no cover
            log.error(e)

    # rename "locationMetadata" resources'
    # "config.special.entries_integration.item_props[n].name" to
    # "config.special.entries_integration.item_props[n].key"
    for res in await db.resources.find({"resource_type": "locationMetadata"}).to_list():
        try:
            for props in res["config"]["special"]["entries_integration"]["item_props"]:
                if "name" not in props:
                    continue
                props["key"] = props["name"]
                del props["name"]
            await db.resources.update_one(
                {"_id": res["_id"]},
                {
                    "$set": {
                        "config.special.entries_integration.item_props": res["config"][
                            "special"
                        ]["entries_integration"]["item_props"]
                    }
                },
            )
        except Exception as e:  # pragma: no cover
            log.error(e)

    # transform "textAnnotation" resources' "config.special.annotations.groups"
    # config field into "config.special.annotations.anno_integration", following
    # the ItemIntegrationConfig model schema
    resources = await db.resources.find({"resource_type": "textAnnotation"}).to_list()
    for res in resources:
        # get data from "config.special.annotations.groups"
        try:
            groups = res["config"]["special"]["annotations"]["groups"] or []
        except KeyError:
            groups = []

        # delete "config.special.annotations.groups"
        await db.resources.update_one(
            {"_id": res["_id"]},
            {"$unset": {"config.special.annotations.groups": ""}},
        )

        # if groups field actually held data, transform it
        await db.resources.update_one(
            {"_id": res["_id"]},
            {
                "$set": {
                    "config.special.annotations.anno_integration.groups": [
                        {
                            "key": group["key"],
                            "translations": group["translations"],
                        }
                        for group in groups
                    ]
                }
            },
        )

        # get aggregations to use for "item_props" below
        aggs = await db.precomputed.find_one(
            {"ref_id": res["_id"], "precomputed_type": "aggregations"}
        )
        aggs = aggs.get("data", []) if aggs else []

        # generate dummy item_props from aggregations
        await db.resources.update_one(
            {"_id": res["_id"]},
            {
                "$set": {
                    "config.special.annotations.anno_integration.item_props": [
                        {
                            "key": agg["key"],
                            "translations": [
                                {
                                    "locale": "*",
                                    "translation": agg["key"],
                                }
                            ],
                        }
                        for agg in aggs
                    ]
                }
            },
        )
