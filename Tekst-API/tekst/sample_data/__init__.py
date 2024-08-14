from os.path import realpath
from pathlib import Path

from bson import json_util

from tekst import db
from tekst.config import TekstConfig, get_config
from tekst.logs import log


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
_SAMPLE_DATA_DIR = Path(realpath(__file__)).parent / "db"


async def insert_sample_data():
    log.info("Inserting sample data...")
    target_collections = ("texts", "locations", "resources", "contents")
    if _cfg.dev_mode:
        target_collections += ("users", "state")
    database = db.get_db()
    # check if any of the target collections contains data
    for collection in target_collections:
        if await database[collection].find_one():  # pragma: no cover
            log.warning(
                f"Found data in collection: {collection}. "
                f"Skipping sample data insertion."
            )
            return
    # insert sample data
    for collection in target_collections:
        log.debug(f"Populating collection with sample data: {collection}...")
        path = _SAMPLE_DATA_DIR / f"{collection}.json"
        data = json_util.loads(path.read_text())
        result = await database[collection].insert_many(data)
        if not result.acknowledged:  # pragma: no cover
            log.error(f"Failed to insert sample data into collection: {collection}")
