from textrig.db import get_client
from textrig.dependencies import get_db_client


def test_globals_integrity(test_app, config):
    uri = config.db.get_uri()
    assert get_client(uri) is get_client(uri)
    assert get_client(uri) is get_db_client(config)
