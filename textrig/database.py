from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
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
    result = await _db[collection].update_one(
        filter={"_id": _to_obj_id(doc_id)},
        update={"$set": _obj_to_dict(updates, exclude_unset=True)},
    )
    return result.acknowledged


async def get(collection: str, doc_id: ObjectId | str) -> dict | None:
    return await _db[collection].find_one({"_id": _to_obj_id(doc_id)})
