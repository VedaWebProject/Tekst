from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient as DatabaseClient
from motor.motor_asyncio import AsyncIOMotorDatabase as Database

from tekst.auth import AccessToken
from tekst.config import TekstConfig, get_config
from tekst.layer_types import layer_types_mgr
from tekst.logging import log
from tekst.models.layer import LayerBaseDocument
from tekst.models.segment import ClientSegmentDocument
from tekst.models.settings import PlatformSettingsDocument
from tekst.models.text import NodeDocument, TextDocument
from tekst.models.unit import UnitBaseDocument
from tekst.models.user import UserDocument


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


async def reset_db():
    """Drops the database"""
    await get_client(_cfg.db_uri).drop_database(_cfg.db_name)


async def init_odm(db: Database) -> None:
    # collect basic models
    models = [
        TextDocument,
        NodeDocument,
        LayerBaseDocument,
        UnitBaseDocument,
        PlatformSettingsDocument,
        ClientSegmentDocument,
        UserDocument,
        AccessToken,
    ]
    # add layer type models
    for lt_class in layer_types_mgr.get_all().values():
        models.append(lt_class.layer_model().document_model())
        models.append(lt_class.get_unit_model().document_model())
    # init beanie ODM
    await init_beanie(database=db, allow_index_dropping=True, document_models=models)
