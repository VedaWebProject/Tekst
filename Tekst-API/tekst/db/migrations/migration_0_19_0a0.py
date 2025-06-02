from tekst.db import Database


async def migration(db: Database) -> None:
    # - add "token.token" to "token.annotations" as "form"
    # - add "token.lb" to "token.annotations" as "eol"
    async for content in db.contents.find({"resource_type": "textAnnotation"}):
        for token in content["tokens"]:
            if token_form := token.get("token"):
                token["annotations"].append({"key": "form", "value": [token_form]})
            if token.get("lb"):
                token["annotations"].append({"key": "eol", "value": ["true"]})
        # replace with updated content doc
        await db.contents.replace_one({"_id": content["_id"]}, content)

    # remove "token" and "lb" fields from text annotation contents' "tokens" objects
    await db.contents.update_many(
        {"resource_type": "textAnnotation"},
        {"$unset": {"tokens.$[].token": 1, "tokens.$[].lb": 1}},
    )
