from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database

from tekst.auth import AccessToken
from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.node import NodeDocument
from tekst.models.resource import ResourceBaseDocument
from tekst.models.segment import ClientSegmentDocument
from tekst.models.settings import PlatformSettingsDocument
from tekst.models.text import TextDocument
from tekst.models.unit import UnitBaseDocument
from tekst.models.user import UserDocument
from tekst.resource_types import resource_types_mgr


_cfg: TekstConfig = get_config()
_db_client: DatabaseClient = None

# _ID_KEY_PATTERN = r"^(id|_id|.*?Id|.*?_id)$"


def _init_client(db_uri: str = None) -> None:
    global _db_client
    if _db_client is None:
        log.info("Initializing database client...")
        _db_client = DatabaseClient(db_uri or _cfg.db_uri)


def get_client(db_uri: str) -> DatabaseClient:
    global _db_client
    _init_client(db_uri)
    return _db_client


async def init_odm(db: Database) -> None:
    # collect basic models
    models = [
        TextDocument,
        NodeDocument,
        ResourceBaseDocument,
        UnitBaseDocument,
        PlatformSettingsDocument,
        ClientSegmentDocument,
        UserDocument,
        AccessToken,
    ]
    # add resource type models
    for lt_class in resource_types_mgr.get_all().values():
        models.append(lt_class.resource_model().document_model())
        models.append(lt_class.unit_model().document_model())
    # init beanie ODM
    await init_beanie(database=db, allow_index_dropping=True, document_models=models)
