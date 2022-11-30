from bson import ObjectId
from humps import camelize, decamelize
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


def for_mongo(obj: dict) -> dict:
    def gen_obj_ids(d: dict) -> dict:
        for k, v in d.items():
            if not isinstance(k, str):
                raise ValueError("Keys sould be strings")
            elif isinstance(v, dict):
                d[k] = gen_obj_ids(v)
            elif k in ("id", "_id") or k.endswith("Id"):
                if ObjectId.is_valid(str(v)):
                    d[k] = ObjectId(str(v))
        return d

    return gen_obj_ids(camelize(obj))


def from_mongo(obj: dict) -> dict:
    def encode_obj_ids(d: dict) -> dict:
        for k, v in d.items():
            if not isinstance(k, str):
                raise ValueError("Keys sould be strings")
            elif isinstance(v, dict):
                d[k] = encode_obj_ids(v)
            elif k in ("id", "_id") or k.endswith("Id"):
                if isinstance(v, ObjectId):
                    d[k] = str(v)
                if k == "_id":
                    d["id"] = d.pop(k)
        return d

    return encode_obj_ids(decamelize(obj))


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
