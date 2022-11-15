import json

import pytest
import requests
from httpx import AsyncClient
from textrig.app import app
from textrig.config import TextRigConfig, get_config
from textrig.db import DatabaseClient, indexes
from textrig.dependencies import get_db_client


"""
pytest fixtures go in here...
"""


@pytest.fixture
def config() -> TextRigConfig:
    """Returns the app config according to passed env vars, env file or defaults"""
    return get_config()


@pytest.fixture
def root_path(config) -> TextRigConfig:
    """Returns the configured app root path"""
    return config.root_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def get_db_client_override(config) -> DatabaseClient:
    """Dependency override for the database client dependency"""
    db_client: DatabaseClient = DatabaseClient(config.db.get_uri())
    await indexes.create_indexes(cfg=config, db_client=db_client)
    yield db_client
    # clean up
    await db_client.drop_database(config.db.name)
    db_client.close()


@pytest.fixture
def test_data(shared_datadir) -> dict:
    """Returns all shared test data"""
    return json.loads((shared_datadir / "test-data.json").read_text())


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
    """Provides an app instance with overridden dependencies"""
    app.dependency_overrides[get_db_client] = lambda: get_db_client_override
    return app


@pytest.fixture
async def test_client(test_app) -> AsyncClient:
    """Returns an asynchronous test client for API testing"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def load_test_data_texts(root_path, test_client, test_data) -> None:
    """Insert test data for texts into testing database"""
    for text in test_data["texts"]:
        await test_client.post(f"{root_path}/text", json=text)


@pytest.fixture
async def load_test_data_nodes(
    root_path, test_client, test_data, load_test_data_texts
) -> None:
    """Insert test data for nodes into testing database"""
    for node in test_data["nodes"]:
        await test_client.post(f"{root_path}/node", json=node)


@pytest.fixture
async def load_test_data_layers(
    root_path, test_client, test_data, load_test_data_nodes
) -> None:
    """Insert test data for layers into testing database"""
    for layer in test_data["layers"]:
        await test_client.post(f"{root_path}/layer", json=layer)


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Prevents outside network access while testing"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
