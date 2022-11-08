import os

from textrig import logging
from textrig.db import get_client
from textrig.dependencies import get_db_client


def test_globals_integrity(config, test_app):
    uri = config.db.get_uri()
    assert get_client(uri) is get_client(uri)
    assert get_client(uri) is get_db_client(config)


def test_logging_setup_without_errors():
    logging.setup_logging()
    logging.log.info("foo bar")
    os.environ["SERVER_SOFTWARE"] = "gunicorn"
    logging.setup_logging()
    logging.log.info("foo bar")
