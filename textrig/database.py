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
_db: Database = _client[_cfg.db.db_name]


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


def _obj_to_dict(obj: BaseModel | dict, exclude_unset: bool = False) -> dict:
    if isinstance(obj, BaseModel):
        return obj.dict(exclude_unset=exclude_unset)
    return obj


async def update(
    collection: str, doc_id: ObjectId | str, updates: BaseModel | dict
) -> bool:
    result: UpdateResult = await _db[collection].update_one(
        filter={"_id": _to_obj_id(doc_id)},
        update={"$set": _obj_to_dict(updates, exclude_unset=True)},
    )
    return result.acknowledged


async def get(collection: str, val: Any, field: str = "_id") -> dict | None:
    if field == "_id" and type(val) is not ObjectId:
        val = _to_obj_id(val)
    return await _db[collection].find_one({field: val})


async def get_all(
    collection: str, example: dict = {}, limit: int = 10
) -> list[BaseModel]:
    cursor = _db[collection].find(example)
    return await cursor.to_list(length=min([limit, 1000]))


async def insert(collection: str, doc: BaseModel) -> dict:
    result: InsertOneResult = await _db[collection].insert_one(
        doc.dict(exclude_none=True)
    )
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create text",
        )
    return await get(collection, result.inserted_id)
