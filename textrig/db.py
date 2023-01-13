import re

# from textrig.logging import log
from beanie import init_beanie
from bson import ObjectId
from humps import camelize
from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from textrig.config import TextRigConfig, get_config
from textrig.layer_types import get_layer_types
from textrig.models.text import Node, NodeUpdate, Text


_cfg: TextRigConfig = get_config()
# _db_client: DatabaseClient = None

_ID_KEY_PATTERN = r"^(id|_id|.*?Id|.*?_id)$"


async def init_db(db_uri: str = None) -> None:
    client = DatabaseClient(db_uri or _cfg.db.get_uri())
    # collect basic models
    models = [
        Text,
        Node,
        NodeUpdate,
    ]
    # add layer type models
    for lt_name, lt_class in get_layer_types().items():
        models.append(lt_class.get_layer_model())
        models.append(lt_class.get_layer_update_model())
        models.append(lt_class.get_unit_model())
        models.append(lt_class.get_unit_update_model())
    # init beanie ODM
    await init_beanie(
        database=client.db_name, allow_index_dropping=True, document_models=models
    )


# def get_client(db_uri: str) -> DatabaseClient:
#     global _db_client
#     init_db(db_uri)
#     return _db_client


def for_mongo(obj: dict) -> dict:
    def gen_obj_ids(d: dict) -> dict:
        out = dict()
        for k, v in d.items():
            if not isinstance(k, str):
                raise ValueError("Keys sould be strings")
            elif isinstance(v, dict):
                out[k] = gen_obj_ids(v)
            elif re.match(_ID_KEY_PATTERN, k):
                if ObjectId.is_valid(str(v)):
                    out[k] = ObjectId(str(v))
                if k == "_id":
                    out[k] = out.pop("_id")
            else:
                out[k] = v

        return out

    return camelize(gen_obj_ids(obj))


# def from_mongo(obj: dict | list[dict]) -> dict:
#     def encode_obj_ids(d: dict) -> dict:
#         out = dict()
#         for k, v in d.items():
#             if not isinstance(k, str):
#                 raise ValueError("Keys sould be strings")
#             elif isinstance(v, dict):
#                 out[k] = encode_obj_ids(v)
#             elif re.match(_ID_KEY_PATTERN, k):
#                 if isinstance(v, ObjectId):
#                     out[k] = str(v)
#                 if k == "_id":
#                     out["id"] = out.pop(k)
#             else:
#                 out[k] = v
#         return out

#     if type(obj) is dict:
#         return encode_obj_ids(obj)
#     elif type(obj) is list:
#         return [encode_obj_ids(o) for o in obj]
#     else:
#         raise TypeError(
#             "The passed object must be of type "
#             f"'dict' or 'list', got '{type(obj).__name__}'"
#         )


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
