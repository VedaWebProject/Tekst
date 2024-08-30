from typing import Any

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database

from tekst.auth import AccessToken
from tekst.config import TekstConfig, get_config
from tekst.logs import log
from tekst.models.bookmark import BookmarkDocument
from tekst.models.content import ContentBaseDocument
from tekst.models.correction import CorrectionDocument
from tekst.models.location import LocationDocument
from tekst.models.message import UserMessageDocument
from tekst.models.platform import PlatformStateDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.segment import ClientSegmentDocument
from tekst.models.text import TextDocument
from tekst.models.user import UserDocument
from tekst.resources import resource_types_mgr
from tekst.tasks import TaskDocument


_db_client: DatabaseClient = None


def _init_db_client(db_uri: str | None = None) -> DatabaseClient:
    global _db_client
    if _db_client is None:
        log.debug("Initializing database client...")
        db_uri = db_uri or get_config().db.uri
        try:
            _db_client = DatabaseClient(db_uri)
        except Exception as e:
            log.critical(f"Could not connect to database at {db_uri}: {e}")
            raise RuntimeError(f"Could not initialize database client: {e}")
    return _db_client


def get_db_client(db_uri: str | None = None) -> DatabaseClient:
    return _init_db_client(db_uri)


async def get_db_status() -> dict[str, Any] | None:
    db_client = get_db_client()
    return await db_client.server_info() if db_client else None


def get_db(
    db_client: Database = get_db_client(), cfg: TekstConfig = get_config()
) -> Database:
    return db_client[cfg.db.name]


async def init_odm(db: Database = get_db()) -> None:
    log.debug("Initializing ODM...")
    # collect basic document models
    models = [
        TextDocument,
        LocationDocument,
        ResourceBaseDocument,
        ContentBaseDocument,
        CorrectionDocument,
        PlatformStateDocument,
        ClientSegmentDocument,
        UserDocument,
        UserMessageDocument,
        BookmarkDocument,
        AccessToken,
        TaskDocument,
    ]
    # add all resource types' resource and content document models
    for lt_class in resource_types_mgr.get_all().values():
        models.append(lt_class.resource_model().document_model())
        models.append(lt_class.content_model().document_model())
    # init beanie ODM
    await init_beanie(
        database=db,
        allow_index_dropping=True,
        document_models=models,
    )


def close() -> None:
    global _db_client
    if _db_client is not None:
        _db_client.close()
