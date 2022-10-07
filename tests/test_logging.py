import os

from textrig import logging


def test_logging_setup_without_errors(testing_config):
    os.environ["DEV_MODE"] = "false"
    logging.setup_logging()
    logging.log.info("foo bar")
    os.environ["DEV_MODE"] = "true"
    logging.setup_logging()
    logging.log.info("foo bar")
    os.environ["SERVER_SOFTWARE"] = "gunicorn"
    logging.setup_logging()
    logging.log.info("foo bar")
    assert True
