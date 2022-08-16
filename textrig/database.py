import motor.motor_asyncio as motor
from textrig.config import TextRigConfig, get_config


_cfg: TextRigConfig = get_config()

# init db connection
_client = motor.AsyncIOMotorClient(_cfg.db.get_uri())
db = _client[_cfg.db.db_name]
