from humps import decamelize

from tekst.db import Database


async def migration(db: Database) -> None:
    for coll_name in await db.list_collection_names():
        async for doc in db[coll_name].find():
            await db[coll_name].replace_one({"_id": doc["_id"]}, decamelize(doc))
