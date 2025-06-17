from tekst.db import Database


async def migration(db: Database) -> None:
    # for each apiCall resource ...
    async for res in db.resources.find({"resource_type": "apiCall"}):
        api_call_cfg = res["config"]["special"].get("api_call")
        if not api_call_cfg:
            continue
        # ... and each content belonging to this resource ...
        async for content in db.contents.find({"resource_id": res["_id"]}):
            content["calls"] = [
                {
                    "key": "default",
                    "endpoint": api_call_cfg["endpoint"],
                    "method": api_call_cfg["method"],
                    "content_type": api_call_cfg["content_type"],
                    "query": content["query"],
                    "transform_context": content["transform_context"],
                }
            ]
            del content["query"]
            del content["transform_context"]
            # replace with updated content doc
            await db.contents.replace_one({"_id": content["_id"]}, content)
        # remove obsolete config entries from resource config
        del res["config"]["special"]["api_call"]
        await db.resources.replace_one({"_id": res["_id"]}, res)
