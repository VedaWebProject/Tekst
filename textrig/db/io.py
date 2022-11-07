from typing import Any, Mapping

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCursor as Cursor
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult
from textrig.models.common import BaseModel
from textrig.utils.strings import keys_snake_to_camel_case


class DbIO:
    def __init__(self, db: Database):
        self._db = db

    def _obj_id(self, obj_id: str | ObjectId) -> ObjectId:

        if isinstance(obj_id, str):
            return ObjectId(obj_id)
        elif isinstance(obj_id, ObjectId):
            return obj_id
        else:
            raise TypeError(
                f"Takes string-like object or ObjectId, {type(obj_id)} given"
            )

    async def count_documents(
        self,
        collection: str,
        filter: Mapping[str, Any],
        max_time_ms: int = 200,
    ) -> int:
        return await self._db[collection].count_documents(
            filter=filter, maxTimeMS=max_time_ms
        )

    async def update(
        self, collection: str, doc_id: ObjectId | str, updates: BaseModel | dict
    ) -> bool:

        if isinstance(updates, BaseModel):
            updates = updates.dict(for_mongo=True)

        result: UpdateResult = await self._db[collection].update_one(
            filter={"_id": self._obj_id(doc_id)},
            update={"$set": updates},
        )

        return result.acknowledged

    async def find_one(
        self, collection: str, value: Any, field: str = "_id"
    ) -> dict | None:

        if field == "id":
            field = "_id"

        if field == "_id":
            try:
                value = self._obj_id(value)
            except Exception:
                return None

        return await self._db[collection].find_one({field: value})

    async def find_one_by_example(self, collection: str, example: dict) -> dict | None:

        example = keys_snake_to_camel_case(example)
        return await self._db[collection].find_one(example)

    async def find(
        self,
        collection: str,
        example: dict = {},
        projection: dict = None,
        limit: int = 10,
        hint: str = None,
        to_list: bool = True,
    ) -> list[dict] | Cursor:

        example = keys_snake_to_camel_case(example)
        cursor = self._db[collection].find(
            example, projection=projection, limit=limit, hint=hint
        )

        if to_list:
            return await cursor.to_list(length=limit if limit > 0 else None)
        else:
            return cursor

    async def insert_one(self, collection: str, doc: BaseModel | dict) -> dict:

        if isinstance(doc, BaseModel):
            doc = doc.dict(for_mongo=True)

        result: InsertOneResult = await self._db[collection].insert_one(doc)

        if not result.acknowledged:
            raise IOError(f"Error inserting document: {str(doc)}")

        return await self.find_one(collection, result.inserted_id)

    async def insert_many(
        self, collection: str, docs: list[BaseModel] | list[dict]
    ) -> list[str]:

        if not type(docs) == list[dict]:
            docs = [d.dict(for_mongo=True) for d in docs]

        result: InsertManyResult = await self._db[collection].insert_many(docs)

        if not result.acknowledged:
            raise IOError(f"Error inserting {len(docs)} documents into DB")

        return [str(doc_id) for doc_id in result.inserted_ids]
