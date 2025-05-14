from tekst.db import Database


async def migration(db: Database) -> None:
    # collect resources with pinned metadata
    pinned_loc_meta_res_ids = set()
    for text in await db.texts.find().to_list():
        pinned_loc_meta_res_ids |= set(text.get("pinned_metadata_ids", []))

    # delete "pinned_metadata_ids" config from all texts
    await db.texts.update_many({}, {"$unset": {"pinned_metadata_ids": ""}})

    # set "embed as tags" to True for collected resources
    await db.resources.update_many(
        {"_id": {"$in": list(pinned_loc_meta_res_ids)}},
        {"$set": {"config.special.embed_as_tags": True}},
    )
