import os

from bson import ObjectId
from textrig import logging
from textrig.db import for_mongo, get_client
from textrig.dependencies import get_db_client


def test_globals_integrity(config):
    uri = config.db.get_uri()
    assert get_client(uri) is get_client(uri)
    assert get_client(uri) is get_db_client(config)


def test_logging_setup_without_errors():
    logging.setup_logging()
    logging.log.info("foo bar")
    os.environ["SERVER_SOFTWARE"] = "gunicorn"
    logging.setup_logging()
    logging.log.info("foo bar")


def test_for_mongo_request():
    req = {
        "id": "637b94cb6bc85f7410a49bc9",
        "_id": "637b94cb6bc85f7410a49bc9",
        "parent_id": "637b94cb6bc85f7410a49bc9",
        "nested": {"id": "637b94cb6bc85f7410a49bc9"},
    }
    req = for_mongo(req)
    assert type(req.get("id")) == ObjectId
    assert type(req.get("_id")) == ObjectId
    assert "parent_id" not in req
    assert "parentId" in req
    assert type(req.get("parentId")) == ObjectId
    assert type(req.get("nested").get("id")) == ObjectId
