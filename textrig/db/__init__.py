from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from textrig.config import TextRigConfig, get_config
from textrig.logging import log


_cfg: TextRigConfig = get_config()
_db_client: DatabaseClient = None


def init_client(db_uri: str = None) -> None:
    global _db_client
    if _db_client is None:
        log.info("Initializing database client")
        _db_client = DatabaseClient(db_uri or _cfg.db.get_uri())


def get_client(db_uri: str) -> DatabaseClient:
    global _db_client
    init_client(db_uri)
    return _db_client


# class __DbClientProvider:
#     def __init__(self):
#         self._client: DatabaseClient = None

#     def __call__(self, db_uri: str) -> DatabaseClient:
#         if self._client is not None:
#             return self._client

#         self._client = DatabaseClient(db_uri)
#         return self._client

#     def close(self):
#         if self._client is not None:
#             self._client.close()


# get_client = __DbClientProvider()
