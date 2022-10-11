# create indexes for "texts" collection
import pymongo
from textrig.db import coll


_index_models = {
    "texts": [
        pymongo.IndexModel([("slug", pymongo.ASCENDING)], name="slug", unique=True)
    ],
    "units": [
        pymongo.IndexModel(
            [
                ("textId", pymongo.ASCENDING),
                ("level", pymongo.ASCENDING),
                ("index", pymongo.ASCENDING),
            ],
            name="textId_level_index",
        ),
        pymongo.IndexModel(
            [
                ("parentId", pymongo.ASCENDING),
            ],
            name="parentId",
        ),
    ],
}


async def create_indexes():

    # create indexes
    for collection, indexes in _index_models.items():
        await coll(collection).create_indexes(indexes)
