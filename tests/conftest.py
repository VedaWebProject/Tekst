from functools import lru_cache

import pytest
from fastapi.testclient import TestClient
from textrig.config import Config, get_config
from textrig.main import app as app_instance


"""
pytest fixtures go in here...
"""


@lru_cache()
def get_config_override():
    """config overrides for tests"""
    return Config(app_name="TextRig Test Instance")


@pytest.fixture
def app():
    """
    Provides an app instance with overridden
    config according to get_config_override()
    """
    app_instance.dependency_overrides[get_config] = get_config_override
    return app_instance


@lru_cache()
@pytest.fixture
def client(app):
    """
    Provides a TestClient instance configured with an app instance
    with overridden config according to get_config_override()
    """
    return TestClient(app)
