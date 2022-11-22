# create indexes for "texts" collection
import pymongo
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from textrig.config import TextRigConfig, get_config
from textrig.dependencies import get_db, get_db_client
from textrig.layer_types import get_layer_types
from textrig.logging import log


def _get_index_models() -> dict:
    return {
        "texts": [
            pymongo.IndexModel([("slug", pymongo.ASCENDING)], name="slug", unique=True)
        ],
        "nodes": [
            pymongo.IndexModel(
                [
                    ("textSlug", pymongo.ASCENDING),
                    ("parentId", pymongo.ASCENDING),
                    ("level", pymongo.ASCENDING),
                    ("index", pymongo.ASCENDING),
                ],
                name="textSlug_parentId_level_index",
                unique=True,
            ),
        ],
        "layers": [
            pymongo.IndexModel(
                [
                    ("textSlug", pymongo.ASCENDING),
                    ("level", pymongo.ASCENDING),
                    ("public", pymongo.ASCENDING),
                ],
                name="textSlug_level_public",
            ),
            pymongo.IndexModel(
                [
                    ("textSlug", pymongo.ASCENDING),
                    ("ownerId", pymongo.ASCENDING),
                ],
                name="textSlug_ownerId",
            ),
        ],
        "units": [
            pymongo.IndexModel(
                [
                    ("layerId", pymongo.ASCENDING),
                    ("nodeId", pymongo.ASCENDING),
                ],
                name="layerId_nodeId",
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
    log.info("Creating database indexes")
    db_client = get_db_client(cfg)
    db: Database = get_db(db_client, cfg)

    # collect common system collection index models
    indexes = _get_index_models()

    # collect layer type unit index models
    for lt_name, lt_class in get_layer_types().items():
        indexes["units"].append(lt_class.get_index_model())

    # create indexes
    for collection, indexes in indexes.items():
        await db[collection].create_indexes(indexes)
