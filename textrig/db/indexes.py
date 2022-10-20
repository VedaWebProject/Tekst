# create indexes for "texts" collection
import pymongo
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from textrig.config import TextRigConfig, get_config
from textrig.dependencies import get_db, get_db_client


_index_models = {
    "texts": [
        pymongo.IndexModel([("slug", pymongo.ASCENDING)], name="slug", unique=True)
    ],
    "units": [
        pymongo.IndexModel(
            [
                ("textSlug", pymongo.ASCENDING),
                ("level", pymongo.ASCENDING),
                ("index", pymongo.ASCENDING),
            ],
            name="textSlug_level_index",
        ),
        pymongo.IndexModel(
            [
                ("textSlug", pymongo.ASCENDING),
                ("parentId", pymongo.ASCENDING),
            ],
            name="textSlug_parentId",
        ),
    ],
}


async def create_indexes(cfg: TextRigConfig = get_config()):
    """
    Creates all necessary database indexes. Unfortunately, because FastAPI dependency
    injection is not available during startup/shutdown events, we cannot properly use
    the DB dependency here. Instead, we're forced to serve the dependency functions
    the config that's passed to this function (which will be "manually" fetched) :(
    """

    db: Database = get_db(get_db_client(cfg), cfg)

    # create indexes
    for collection, indexes in _index_models.items():
        await db[collection].create_indexes(indexes)
