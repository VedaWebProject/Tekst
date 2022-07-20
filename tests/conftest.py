from functools import lru_cache

import pytest
from fastapi.testclient import TestClient
from textrig.config import Config, get_config
from textrig.main import app


# pytest fixtures go here ...


@lru_cache()
def get_config_override():
    """config overrides for tests"""
    return Config(app_name="suppe")


@lru_cache()
@pytest.fixture
def test_app():
    """
    Provides an app instance with overridden
    config according to get_config_override()
    """
    app.dependency_overrides[get_config] = get_config_override
    return app


@lru_cache()
@pytest.fixture
def test_client(test_app):
    """
    Provides a TestClient instance configured with an app instance
    with overridden config according to get_config_override()
    """
    return TestClient(test_app)
