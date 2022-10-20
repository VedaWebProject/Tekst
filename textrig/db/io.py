from typing import Any, Type

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult
from textrig.models.common import BaseModel
from textrig.utils.strings import keys_snake_to_camel_case


class DbIO:
    def __init__(self, db: Database):
        self._db = db

    def _obj_id(self, obj_id: str | ObjectId) -> ObjectId:

        if type(obj_id) is not ObjectId:
            return ObjectId(obj_id)

        return obj_id

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
        self,
        collection: str,
        value: Any,
        field: str = "_id",
        model: Type[BaseModel] = None,
    ) -> dict | None | BaseModel:

        if field == "id":
            field = "_id"

        if field == "_id":
            value = self._obj_id(value)

        data = await self._db[collection].find_one({field: value})

        if not data:
            return None

        if model:
            return model(**data)

        return data

    async def find_one_by_example(self, collection: str, example: dict) -> dict | None:

        example = keys_snake_to_camel_case(example)
        return await self._db[collection].find_one(example)

    async def find(
        self, collection: str, example: dict = {}, limit: int = 10
    ) -> list[dict]:

        example = keys_snake_to_camel_case(example)
        cursor = self._db[collection].find(example)
        return await cursor.to_list(length=min([limit, 1000]))

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
