from typing import Any

from bson import ObjectId
from humps import camelize
from motor.motor_asyncio import AsyncIOMotorCursor as Cursor
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from pymongo.results import InsertManyResult, InsertOneResult, UpdateResult
from textrig.models.common import TextRigBaseModel


class DbIO:
    """
    A wrapper class for all IO operations through the MongoDB database

    This is meant to be used as a dependency for FastAPI dependency injection.
    The methods wrap and extend Motor/pymongo/MongoDB functionality to ease usage
    in the context of this project.
    """

    def __init__(self, db: Database):
        self._db = db

    def _obj_id(self, obj_id: str | ObjectId) -> ObjectId:
        """
        Normalizes IDs to be ObjectId instances

        Takes a string or ObjectId and returns an ObjectId.
        Raises an error if any other type is passed.

        :param obj_id: The ID to normalize
        :type obj_id: str | ObjectId
        :raises TypeError: Raised if any unexpected type is passed
        :return: An ObjectId instance representing the passed ID
        :rtype: ObjectId
        """
        # check type of given ID, return ObjectId in any case
        if isinstance(obj_id, str):
            return ObjectId(obj_id)
        elif isinstance(obj_id, ObjectId):
            return obj_id
        else:
            raise TypeError(
                f"Takes string-like object or ObjectId; {type(obj_id)} given"
            )

    async def count_documents(
        self,
        collection: str,
        filter: dict[str, Any],
        max_time_ms: int = 200,
    ) -> int:
        """
        Counts documents matching the given criteria

        :param collection: Name of the target collection
        :type collection: str
        :param filter: Criteria for the documents to match
        :type filter: dict[str, Any]
        :param max_time_ms: Max time for counting in ms, defaults to 200
        :type max_time_ms: int, optional
        :return: Number of counted documents
        :rtype: int
        """
        return await self._db[collection].count_documents(
            filter=filter, maxTimeMS=max_time_ms
        )

    async def update(
        self,
        collection: str,
        updates: TextRigBaseModel | dict,
        doc_id: ObjectId | str = None,
    ) -> str:
        """
        Updates a document in the database

        :param collection: Name of the target collection
        :type collection: str
        :param updates: The updated values
        :type updates: TextRigBaseModel | dict
        :param doc_id: ID of the target document
                       (only needed if passed update object
                       doesn't have an 'id' or '_id' field)
        :type doc_id: ObjectId | str
        :return: ID of updated document or None if operation unsuccessful
        :rtype: str
        """
        # serialize model instance if applicable
        if isinstance(updates, TextRigBaseModel):
            updates = updates.dict(for_mongo=True)
        # check if and how ID was passed
        if doc_id is None:
            doc_id = updates.get("id", updates.get("_id", None))
            if doc_id is None:
                return None
        # update document
        result: UpdateResult = await self._db[collection].update_one(
            filter={"_id": self._obj_id(doc_id)},
            update={"$set": updates},
        )
        # return ID if operation was successful, None otherwise
        return str(doc_id) if result.acknowledged else None

    async def find_one(
        self, collection: str, value: Any, field: str = "_id"
    ) -> dict | None:
        """
        Finds a single matching document by a single property value
        in the target collection

        :param collection: Name of the target collection
        :type collection: str
        :param value: Value to look for
        :type value: Any
        :param field: Field to look for, defaults to "_id"
        :type field: str, optional
        :return: The document data or None if nothing was found
        :rtype: dict | None
        """
        # use "_id" instead of "id" if used as field
        if field == "id":
            field = "_id"
        # init ObjectId for ID passed as string
        if field == "_id":
            try:
                value = self._obj_id(value)
            except Exception:
                return None
        # return whatever the db can find (may be None)
        return await self._db[collection].find_one({field: value})

    async def find_one_by_example(self, collection: str, example: dict) -> dict | None:
        """
        Finds a single document by example data in the target collection

        :param collection: Name of the target collection
        :type collection: str
        :param example: Example data to describe the document to find
        :type example: dict
        :return: Document data or None if nothing is found
        :rtype: dict | None
        """
        example = camelize(example)
        return await self._db[collection].find_one(example)

    async def find(
        self,
        collection: str,
        example: dict = None,
        projection: dict = None,
        limit: int = 10,
        hint: str = None,
        to_list: bool = True,
    ) -> list[dict] | Cursor:
        """
        Finds multiple documents from the target collection by example

        :param collection: Name of the target collection
        :type collection: str
        :param example: Example data, defaults to None
        :type example: dict, optional
        :param projection: A list describing the fields to include or a dict
                           describing the fields to include (True) or exclude (False),
                           defaults to None
        :type projection: dict | list, optional
        :param limit: Max number of documents to retrieve, defaults to 10
        :type limit: int, optional
        :param hint: Index name to hint to using a certain index, defaults to None
        :type hint: str, optional
        :param to_list: Whether a static list or an interactive database cursor should
                        be returned, defaults to True
        :type to_list: bool, optional
        :return: List of document data sets or database cursor
        :rtype: list[dict] | Cursor
        """
        # force camel case on example keys
        example = camelize(example)
        # get cursor from db
        cursor = self._db[collection].find(
            example, projection=projection, limit=limit, hint=hint
        )
        # return list or cursor
        if to_list:
            return await cursor.to_list(length=limit if limit > 0 else None)
        else:
            return cursor

    async def insert_one(self, collection: str, doc: TextRigBaseModel | dict) -> dict:
        """
        Inserts a single document into the database

        :param collection: Name of the target collection
        :type collection: str
        :param doc: The document to insert
        :type doc: TextRigBaseModel | dict
        :raises IOError: Raised if insert operation fails
        :return: The full inserted document, including the given ID
        :rtype: dict
        """
        # serialize model instance to dict
        if isinstance(doc, TextRigBaseModel):
            doc = doc.dict(for_mongo=True)
        # insert into db
        result: InsertOneResult = await self._db[collection].insert_one(doc)
        # check result
        if not result.acknowledged:
            raise IOError(f"Error inserting document: {str(doc)}")
        # return entire inserted document (get from db)
        return await self.find_one(collection, result.inserted_id)

    async def insert_many(
        self, collection: str, docs: list[TextRigBaseModel] | list[dict]
    ) -> list[str]:
        """
        Inserts multiple documents into the database

        :param collection: Name of the target collection
        :type collection: str
        :param docs: List of documents to insert
        :type docs: list[TextRigBaseModel] | list[dict]
        :raises IOError: Raised if insert operation fails
        :return: List of IDs of the inserted documents
        :rtype: list[str]
        """
        # serialize model instances to dicts
        if not type(docs) == list[dict]:
            docs = [d.dict(for_mongo=True) for d in docs]
        # insert into db
        result: InsertManyResult = await self._db[collection].insert_many(docs)
        # check result
        if not result.acknowledged:
            raise IOError(f"Error inserting {len(docs)} documents into DB")
        # return IDs of inserted documents
        return [str(doc_id) for doc_id in result.inserted_ids]
