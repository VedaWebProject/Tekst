from tekst.db import Database


async def migration(db: Database) -> None:
    # add location ID to all correction model instances
    resources_by_id = {res["_id"]: res for res in await db.resources.find({}).to_list()}
    async for corr in db.corrections.find({}):
        res = resources_by_id[corr["resource_id"]]
        loc = await db.locations.find_one(
            {
                "text_id": res["text_id"],
                "level": res["level"],
                "position": corr["position"],
            }
        )
        await db.corrections.update_one(
            {"_id": corr["_id"]}, {"$set": {"location_id": loc["_id"]}}
        )
    # delete precomputed resource coverage data
    await db.precomputed.delete_many({"precomputed_type": "coverage"})
