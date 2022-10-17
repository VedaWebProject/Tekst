import json

import pytest
import requests
from fastapi.testclient import TestClient
from textrig.app import get_app
from textrig.config import TextRigConfig, get_config
from textrig.db import DatabaseClient, get_client
from textrig.dependencies import get_db_client
from textrig.models.text import Text


"""
pytest fixtures go in here...
"""


def get_db_client_override() -> DatabaseClient:
    cfg: TextRigConfig = get_config()
    db_client = get_client(cfg.db.get_uri())
    return db_client


@pytest.fixture
def sample_data(shared_datadir) -> dict:
    return json.loads((shared_datadir / "sample-data.json").read_text())


@pytest.fixture
def config() -> TextRigConfig:
    return get_config()


@pytest.fixture
def base_url(config) -> str:
    return f"http://{config.dev_srv_host}:{config.dev_srv_port}{config.root_path}"


@pytest.fixture
def test_app():
    """
    Provides an app instance with overridden dependencies
    """
    app = get_app()
    app.dependency_overrides[get_db_client] = get_db_client_override
    return app


@pytest.fixture
def test_client(test_app, base_url):
    """
    Provides a TestClient instance configured with an app instance
    """
    return TestClient(app=test_app, base_url=base_url)


@pytest.fixture
def dummy_data_text(sample_data) -> Text:
    return Text(**sample_data["texts"][0])


@pytest.fixture
def dummy_data_texts(sample_data) -> Text:
    return [Text(**t) for t in sample_data["texts"]]


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
