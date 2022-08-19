from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database
from textrig.config import TextRigConfig, get_config


_cfg: TextRigConfig = get_config()

# init db connection
_client: DatabaseClient = DatabaseClient(_cfg.db.get_uri())
_db: Database = _client[_cfg.db.db_name]


# database object getter for use as a dependency
def get_db() -> Database:
    return _db
