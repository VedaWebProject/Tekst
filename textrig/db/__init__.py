from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorCollection as Collection
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from textrig.config import TextRigConfig, get_config


_cfg: TextRigConfig = get_config()

client: DatabaseClient = DatabaseClient(_cfg.db.get_uri())
db: Database = client[_cfg.db.name]


def coll(name: str) -> Collection:
    return db[name]
