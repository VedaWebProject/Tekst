import json

import pytest
import requests
from httpx import AsyncClient
from textrig.app import app
from textrig.config import TextRigConfig, get_config
from textrig.db import DatabaseClient
from textrig.dependencies import get_db_client
from textrig.models.text import Text


"""
pytest fixtures go in here...
"""


@pytest.fixture
def config() -> TextRigConfig:
    return get_config()


@pytest.fixture
def root_path(config) -> TextRigConfig:
    return config.root_path


@pytest.fixture
async def get_db_client_override(config) -> DatabaseClient:
    db_client: DatabaseClient = DatabaseClient(config.db.get_uri())
    yield db_client
    # clean up
    await db_client.drop_database(config.db.name)
    db_client.close()


@pytest.fixture
def sample_data(shared_datadir) -> dict:
    return json.loads((shared_datadir / "sample-data.json").read_text())


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# @pytest.fixture(scope="session")
# def event_loop():
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture
async def test_app(get_db_client_override):
    """
    Provides an app instance with overridden dependencies
    """
    app.dependency_overrides[get_db_client] = lambda: get_db_client_override
    return app


@pytest.fixture
async def test_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


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
