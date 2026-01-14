from tekst.db import Database


async def migration(db: Database) -> None:
    for content in await db.contents.find({}).to_list():
        if content.get("authors_comment"):
            content["comments"] = content.get("comments", [])
            content["comments"].append(
                {"by": "Author", "comment": content["authors_comment"]}
            )
            del content["authors_comment"]
        if content.get("editors_comments"):
            content["comments"] = content.get("comments", [])
            content["comments"].extend(content["editors_comments"])
            del content["editors_comments"]
        await db.contents.replace_one({"_id": content["_id"]}, content)
