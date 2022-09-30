from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from pymongo.results import InsertOneResult, UpdateResult
from textrig.config import TextRigConfig, get_config
from textrig.models.common import BaseModel


_cfg: TextRigConfig = get_config()

# init db connection
_client: DatabaseClient = DatabaseClient(_cfg.db.get_uri())
_db: Database = _client[_cfg.db.name]


# database object getter for use as a dependency
def get_db() -> Database:
    return _db


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
    result: UpdateResult = await _db[collection].update_one(
        filter={"_id": _to_obj_id(doc_id)},
        update={"$set": updates.mongo(exclude_unset=True)},
    )
    return result.acknowledged


async def get(collection: str, value: Any, field: str = "_id") -> dict | None:
    if field == "_id" and type(value) is not ObjectId:
        value = _to_obj_id(value)
    return await _db[collection].find_one({field: value})


async def get_by_example(collection: str, example: dict) -> dict | None:
    return await _db[collection].find_one(example)


async def get_all(
    collection: str, example: dict = {}, limit: int = 10
) -> list[BaseModel]:
    cursor = _db[collection].find(example)
    return await cursor.to_list(length=min([limit, 1000]))


async def insert(collection: str, doc: BaseModel | dict) -> dict:
    if isinstance(doc, BaseModel):
        doc = doc.mongo(exclude_unset=True)
    result: InsertOneResult = await _db[collection].insert_one(doc)
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create text",
        )
    return await get(collection, result.inserted_id)
