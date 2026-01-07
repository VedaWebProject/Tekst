from tekst.db import Database


async def migration(db: Database) -> None:
    for resource in await db.resources.find({}).to_list():
        if resource.get("owner_id"):
            resource["owner_ids"] = [resource["owner_id"]]
            del resource["owner_id"]
            await db.resources.replace_one({"_id": resource["_id"]}, resource)
