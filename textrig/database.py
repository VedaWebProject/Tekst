from typing import Any, Type

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult
from textrig.config import TextRigConfig, get_config
from textrig.models.common import BaseModel


_cfg: TextRigConfig = get_config()

# init db connection
_client: DatabaseClient = DatabaseClient(_cfg.db.get_uri())
_db: Database = _client[_cfg.db.name]


# database object getter for use as a dependency
def get_db() -> Database:

    return _db


async def init() -> None:

    # create indexes for "texts" collection
    await _db["texts"].create_indexes(
        [pymongo.IndexModel([("slug", pymongo.ASCENDING)], name="slug", unique=True)]
    )

    # create indexes for "units" collection
    await _db["units"].create_indexes(
        [
            pymongo.IndexModel(
                [
                    ("text", pymongo.ASCENDING),
                    ("level", pymongo.ASCENDING),
                    ("index", pymongo.ASCENDING),
                ],
                name="text_level_index",
            ),
            pymongo.IndexModel(
                [
                    ("parent", pymongo.ASCENDING),
                ],
                name="parent",
            ),
        ]
    )


def _to_obj_id(obj_id: str | ObjectId) -> ObjectId:

    if type(obj_id) is not ObjectId:
        try:
            obj_id = ObjectId(obj_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID",
            )

    return obj_id


async def update(
    collection: str, doc_id: ObjectId | str, updates: BaseModel | dict
) -> bool:

    if isinstance(update, BaseModel):
        updates = updates.dict(for_mongo=True)

    result: UpdateResult = await _db[collection].update_one(
        filter={"_id": _to_obj_id(doc_id)},
        update={"$set": updates},
    )

    return result.acknowledged


async def get(
    collection: str, value: Any, field: str = "_id", model: Type[BaseModel] = None
) -> dict | None | BaseModel:

    if field == "id":
        field = "_id"

    if field == "_id":
        value = _to_obj_id(value)

    data = await _db[collection].find_one({field: value})

    if not data:
        return None

    if model:
        return model(**data)

    return data


async def get_by_example(collection: str, example: dict) -> dict | None:

    return await _db[collection].find_one(example)


async def get_all(
    collection: str, example: dict = {}, limit: int = 10
) -> list[BaseModel]:

    cursor = _db[collection].find(example)
    return await cursor.to_list(length=min([limit, 1000]))


async def insert(collection: str, doc: BaseModel | dict) -> dict:

    if isinstance(doc, BaseModel):
        doc = doc.dict(for_mongo=True)

    result: InsertOneResult = await _db[collection].insert_one(doc)

    if not result.acknowledged:
        raise IOError(f"Error inserting document: {str(doc)}")

    return await get(collection, result.inserted_id)


async def insert_many(collection: str, docs: list[BaseModel] | list[dict]) -> list[str]:

    if not type(docs) == list[dict]:
        docs = [d.dict(for_mongo=True) for d in docs]

    result: InsertManyResult = await _db[collection].insert_many(docs)

    if not result.acknowledged:
        raise IOError(f"Error inserting {len(docs)} documents into DB")

    return [str(doc_id) for doc_id in result.inserted_ids]
