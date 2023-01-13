import json

import pytest
import requests
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from textrig.app import app
from textrig.config import TextRigConfig, get_config


"""
pytest fixtures go in here...
"""


@pytest.fixture(scope="session")
def config() -> TextRigConfig:
    """Returns the app config according to passed env vars, env file or defaults"""
    return get_config()


@pytest.fixture(scope="session")
def root_path(config) -> TextRigConfig:
    """Returns the configured app root path"""
    return config.root_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


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
async def test_app(config):
    """Provides an app instance with overridden dependencies"""
    async with LifespanManager(app):
        yield app


@pytest.fixture
async def test_client(test_app) -> AsyncClient:
    """Returns an asynchronous test client for API testing"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def insert_test_data(root_path, test_client, test_data) -> callable:
    """
    Returns an asynchronous function to load
    test data for certain database collections
    """

    async def _insert_test_data(*collections: str) -> None:
        for collection in collections:
            for doc in test_data[collection]:
                endpoint = f"{root_path}/{collection}"
                if collection == "layers":
                    endpoint += f"/{doc['layer_type']}"
                await test_client.post(endpoint, json=doc)

    return _insert_test_data


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Prevents outside network access while testing"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
