from collections.abc import Iterator
from tempfile import TemporaryDirectory

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase as Database

from tekst.config import TekstConfig, get_config
from tekst.db import DatabaseClient, get_client


def get_cfg() -> TekstConfig:
    return get_config()


def get_db_client(cfg: TekstConfig = Depends(get_cfg)) -> DatabaseClient:
    return get_client(cfg.db_get_uri())


def get_db(
    db_client: Database = Depends(get_db_client), cfg: TekstConfig = Depends(get_cfg)
) -> Database:
    return db_client[cfg.db_name]


async def get_temp_dir() -> Iterator[str]:
    dir = TemporaryDirectory()
    try:
        yield dir.name
    finally:
        del dir
