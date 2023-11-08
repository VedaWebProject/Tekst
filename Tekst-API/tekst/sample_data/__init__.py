from os import environ
from os.path import realpath
from pathlib import Path

from bson import json_util

from tekst.config import TekstConfig, get_config
from tekst.dependencies import get_db_client
from tekst.logging import log


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
_SAMPLE_DATA_DIR = Path(realpath(__file__)).parent / "db"


async def insert_sample_data():
    if environ.get("TESTING", False):
        return
    target_collections = ("texts", "nodes", "layers", "units")
    db = get_db_client()[_cfg.db_name]
    # check if any of the target collections contains data
    for collection in target_collections:
        if await db[collection].find_one():
            log.warning(
                f"Found data in collection: {collection}. "
                f"Skipping sample data insertion."
            )
            return
    # insert sample data
    for collection in target_collections:
        log.info(f"Populating collection with sample data: {collection}...")
        path = _SAMPLE_DATA_DIR / f"{collection}.json"
        data = json_util.loads(path.read_text())
        result = await db[collection].insert_many(data)
        if not result.acknowledged:
            log.error(f"Failed to insert sample data into collection: {collection}")
