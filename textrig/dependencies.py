from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as Database

from textrig.config import TextRigConfig, get_config
from textrig.db import DatabaseClient, get_client


def get_cfg() -> TextRigConfig:
    return get_config()


def get_db_client(cfg: TextRigConfig = Depends(get_cfg)) -> DatabaseClient:
    return get_client(cfg.db.get_uri())


def get_db(
    db_client: Database = Depends(get_db_client), cfg: TextRigConfig = Depends(get_cfg)
) -> Database:
    return db_client[cfg.db.name]
