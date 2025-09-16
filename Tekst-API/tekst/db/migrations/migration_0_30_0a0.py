from tekst.db import Database


async def migration(db: Database) -> None:
    async for content in db.contents.find({}):
        if not content.get("editors_comment"):
            continue
        content["editors_comments"] = [
            {"by": "???", "comment": content["editors_comment"]}
        ]
        del content["editors_comment"]
        # replace with updated content doc
        await db.contents.replace_one({"_id": content["_id"]}, content)
