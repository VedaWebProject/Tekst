import contextlib

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import requests

from asgi_lifespan import LifespanManager
from bson import ObjectId, json_util
from httpx import AsyncClient, Response
from humps import camelize
from tekst.app import app
from tekst.auth import _create_user
from tekst.config import TekstConfig, get_config
from tekst.db import DatabaseClient
from tekst.dependencies import get_db_client
from tekst.models.user import UserCreate


"""
pytest fixtures go in here...
"""


@pytest.fixture(scope="session")
def config() -> TekstConfig:
    """Returns the app config according to passed env vars, env file or defaults"""
    return get_config()


@pytest.fixture(scope="session")
def api_path(config) -> TekstConfig:
    """Returns the configured app root path"""
    return config.api_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def get_sample_data_path(request) -> Callable[[str], Path]:
    """Returns the absolute path to a file relative to tests/data"""

    def _get_sample_data_path(rel_path: str) -> Path:
        datadir = Path(request.config.rootdir) / "tekst/sample_data"
        return datadir / rel_path

    return _get_sample_data_path


@pytest.fixture
def get_sample_data(get_sample_data_path) -> Callable[[str], Any]:
    """Returns the object representation of a JSON file relative to tests/data"""

    def _get_sample_data(rel_path: str, for_http: bool = False) -> Any:
        path = get_sample_data_path(rel_path)
        data = json_util.loads(path.read_text())
        if for_http:
            data = camelize(
                [
                    {k: str(v) if isinstance(v, ObjectId) else v for k, v in o.items()}
                    for o in data
                ]
            )
        return data

    return _get_sample_data


# @pytest.fixture(scope="session")
# def event_loop():
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session")
async def get_db_client_override(config) -> DatabaseClient:
    """Dependency override for the database client dependency"""
    db_client: DatabaseClient = DatabaseClient(config.db_uri)
    yield db_client
    # close db connection
    db_client.close()


@pytest.fixture(scope="session")
async def test_app(config, get_db_client_override):
    """Provides an app instance with overridden dependencies"""
    app.dependency_overrides[get_db_client] = lambda: get_db_client_override
    async with LifespanManager(app):
        yield app
    # cleanup data
    await get_db_client_override.drop_database(config.db_name)


@pytest.fixture
async def test_client(test_app, config) -> AsyncClient:
    """Returns an asynchronous test client for API testing"""
    async with AsyncClient(
        app=test_app, base_url=f"{config.server_url}{config.api_path}"
    ) as client:
        yield client


@pytest.fixture
async def reset_db(get_db_client_override, config):
    for collection in ("texts", "nodes", "layers", "units", "users"):
        await get_db_client_override[config.db_name][collection].drop()


@pytest.fixture
async def insert_sample_data(config, reset_db, get_sample_data) -> Callable:
    """
    Returns an asynchronous function to insert
    test data into their respective database collections
    """

    async def _insert_sample_data(*collections: str) -> dict[str, list[str]]:
        db = get_db_client()[config.db_name]
        ids = dict()
        for collection in collections:
            result = await db[collection].insert_many(
                get_sample_data(f"db/{collection}.json")
            )
            if not result.acknowledged:
                raise Exception(f"Failed to insert test {collection}")
            ids[collection] = [str(id_) for id_ in result.inserted_ids]
        return ids

    return _insert_sample_data


@pytest.fixture
def get_fake_user() -> Callable:
    def _get_fake_user(alternative: bool = False):
        return dict(
            email="foo@bar.de" if not alternative else "bar@foo.de",
            username="test_user" if not alternative else "test_user2",
            password="poiPOI098",
            first_name="Foo",
            last_name="Bar",
            affiliation="Some Institution",
        )

    return _get_fake_user


@pytest.fixture
async def register_test_user(get_fake_user) -> Callable:
    async def _register_test_user(
        *,
        is_active: bool = True,
        is_verified: bool = True,
        is_superuser: bool = False,
        alternative: bool = False,
    ) -> dict:
        user_data = get_fake_user(alternative=alternative)
        user = UserCreate(**user_data)
        user.is_active = is_active
        user.is_verified = is_verified
        user.is_superuser = is_superuser
        created_user = await _create_user(user)
        return {"id": str(created_user.id), **user_data}

    return _register_test_user


@pytest.fixture
async def get_session_cookie(
    config, test_client, api_path, status_fail_msg
) -> Callable:
    async def _get_session_cookie(user_data: dict) -> dict:
        payload = {"username": user_data["email"], "password": user_data["password"]}
        resp = await test_client.post(
            "/auth/cookie/login",
            data=payload,
        )
        assert resp.status_code == 204, status_fail_msg(204, resp)
        assert resp.cookies.get(config.security_auth_cookie_name)
        return resp.cookies

    return _get_session_cookie


@pytest.fixture(scope="session")
def status_fail_msg() -> Callable:
    def _status_fail_msg(expected_status: int, response: Response) -> tuple[bool, str]:
        resp_json = "No JSON response data."
        with contextlib.suppress(Exception):
            resp_json = response.json()
        return (
            f"HTTP {response.status_code} (expected: {expected_status})"
            f" -- {resp_json}"
        )

    return _status_fail_msg


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Prevents outside network access while testing"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
