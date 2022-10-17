from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient


_db_client: DatabaseClient = None


def init_client(db_uri: str):
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient(db_uri)


def get_client(db_uri: str):
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
