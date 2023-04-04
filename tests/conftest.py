import json

import pytest
import requests

from asgi_lifespan import LifespanManager
from httpx import AsyncClient, Response
from textrig.app import app
from textrig.auth import UserCreate, _create_user
from textrig.config import TextRigConfig, get_config
from textrig.db import DatabaseClient
from textrig.dependencies import get_db_client
from textrig.layer_types import get_layer_type
from textrig.models.text import NodeDocument, TextDocument


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


@pytest.fixture(scope="session")
async def get_db_client_override(config) -> DatabaseClient:
    """Dependency override for the database client dependency"""
    db_client: DatabaseClient = DatabaseClient(config.db.get_uri())
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
    await get_db_client_override.drop_database(config.db.name)


@pytest.fixture
async def test_client(test_app) -> AsyncClient:
    """Returns an asynchronous test client for API testing"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def reset_db(get_db_client_override, config):
    for collection in ("texts", "nodes", "layers", "units", "users"):
        await get_db_client_override[config.db.name][collection].drop()


@pytest.fixture
async def insert_test_data(test_app, reset_db, root_path, test_data) -> callable:
    """
    Returns an asynchronous function to insert
    test data into their respective database collections
    """

    async def _insert_test_data(*collections: str) -> str | None:
        if "texts" in collections:
            text = TextDocument(**test_data["texts"][0])
            await text.create()
        if "nodes" in collections:
            for doc in test_data["nodes"]:
                await NodeDocument(text_id=text.id, **doc).create()
        if "layers" in collections:
            for doc in test_data["layers"]:
                layer_model = get_layer_type(doc["layerType"]).get_layer_model()
                layer_document_model = layer_model.get_document_model()
                await layer_document_model(text_id=text.id, **doc).create()

        return str(text.id) if text else None

    return _insert_test_data


@pytest.fixture
def new_user_data() -> dict:
    return dict(
        email="foo@bar.de",
        username="test_user",
        password="poiPOI098",
        first_name="Foo",
        last_name="Bar",
    )


@pytest.fixture
async def register_test_user(new_user_data) -> callable:
    async def _register_test_user(superuser: bool = False) -> dict:
        user = UserCreate(**new_user_data)
        user.is_active = True
        user.is_verified = True
        user.is_superuser = superuser
        created_user = await _create_user(user)
        return {"id": str(created_user.id), **new_user_data}

    return _register_test_user


@pytest.fixture
async def get_session_cookie(
    config, test_client, root_path, status_fail_msg
) -> callable:
    async def _get_session_cookie(user_data: dict) -> dict:
        endpoint = f"{root_path}/auth/cookie/login"
        payload = {"username": user_data["email"], "password": user_data["password"]}
        resp = await test_client.post(
            endpoint,
            data=payload,
        )
        assert resp.status_code == 200, status_fail_msg(200, resp)
        assert resp.cookies.get(config.security.auth_cookie_name)
        return resp.cookies

    return _get_session_cookie


@pytest.fixture(scope="session")
def status_fail_msg() -> callable:
    def _status_fail_msg(expected_status: int, response: Response) -> tuple[bool, str]:
        resp_json = "No JSON response data."
        try:
            resp_json = response.json()
        except Exception:
            pass
        return (
            f"HTTP {response.status_code} (expected: {expected_status})"
            f" -- {resp_json}"
        )

    return _status_fail_msg


# @pytest.fixture(scope="session")
# def json_compat() -> callable:
#     """
#     Returns a function that forces JSON encodability of the passed object.
#     """

#     def _json_compat(obj):
#         if isinstance(obj, dict):
#             return {str(k): _json_compat(v) for k, v in obj.items()}
#         elif isinstance(obj, list):
#             return [_json_compat(i) for i in obj]
#         else:
#             try:
#                 json.dumps(obj)
#             except Exception:
#                 return str(obj)
#             return obj

#     return _json_compat


@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    """Prevents outside network access while testing"""

    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
