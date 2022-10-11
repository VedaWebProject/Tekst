from typing import Any, Type

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult
from textrig.config import TextRigConfig, get_config
from textrig.db import coll
from textrig.logging import log
from textrig.models.common import BaseModel
from textrig.utils.strings import keys_snake_to_camel_case


_cfg: TextRigConfig = get_config()


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

    result: UpdateResult = await coll(collection).update_one(
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

    data = await coll(collection).find_one({field: value})

    if not data:
        return None

    if model:
        return model(**data)

    return data


async def get_one(collection: str, example: dict) -> dict | None:

    example = keys_snake_to_camel_case(example)
    log.debug(f"Get one by example: {example}")

    return await coll(collection).find_one(example)


async def get_many(collection: str, example: dict = {}, limit: int = 10) -> list[dict]:

    example = keys_snake_to_camel_case(example)
    log.debug(f"Get many by example: {example} (limit: {limit})")

    cursor = coll(collection).find(example)
    return await cursor.to_list(length=min([limit, 1000]))


async def insert(collection: str, doc: BaseModel | dict) -> dict:

    if isinstance(doc, BaseModel):
        doc = doc.dict(for_mongo=True)

    result: InsertOneResult = await coll(collection).insert_one(doc)

    if not result.acknowledged:
        raise IOError(f"Error inserting document: {str(doc)}")

    return await get(collection, result.inserted_id)


async def insert_many(collection: str, docs: list[BaseModel] | list[dict]) -> list[str]:

    if not type(docs) == list[dict]:
        docs = [d.dict(for_mongo=True) for d in docs]

    result: InsertManyResult = await coll(collection).insert_many(docs)

    if not result.acknowledged:
        raise IOError(f"Error inserting {len(docs)} documents into DB")

    return [str(doc_id) for doc_id in result.inserted_ids]
