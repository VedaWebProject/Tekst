from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

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
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def wrong_id() -> str:
    return "badab001337d00d42b00b1e5"


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
        # set XSRF header and cookie if server sends XSRF cookie
        resp = await client.get("/")
        xsrf_token = resp.cookies.get("XSRF-TOKEN")
        if xsrf_token:
            client.headers.setdefault("X-XSRF-TOKEN", xsrf_token)
            client.cookies.setdefault("XSRF-TOKEN", xsrf_token)
        # yield client instance
        yield client


@pytest.fixture(autouse=True)
async def run_before_and_after_each_test_case(get_db_client_override, config):
    """Fixture to execute asserts before and after a test is run"""
    ### before test case
    # clear DB collections
    for collection in ("texts", "nodes", "resources", "contents", "settings", "users"):
        await get_db_client_override[config.db_name][collection].delete_many({})
    ### run test case
    yield  # test case running now
    ### after test cae
    # ...


@pytest.fixture
async def insert_sample_data(config, get_sample_data) -> Callable:
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
    def _get_fake_user(suffix: str = ""):
        return dict(
            email=f"user{suffix}@foo.de",
            username=f"user{suffix}",
            password="poiPOI098",
            name="Foo Bar",
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
    ) -> dict:
        suffix = (
            f"{'a' if is_active else 'x'}"
            f"{'v' if is_verified else 'x'}"
            f"{'s' if is_superuser else 'x'}"
        )
        user_data = get_fake_user(suffix=suffix)
        user = UserCreate(**user_data)
        user.is_active = is_active
        user.is_verified = is_verified
        user.is_superuser = is_superuser
        created_user = await _create_user(user)
        return {"id": str(created_user.id), **user_data}

    return _register_test_user


@pytest.fixture
async def logout(config, test_client: AsyncClient) -> Callable:
    async def _logout() -> None:
        await test_client.post("/auth/cookie/logout")
        test_client.cookies.delete(name=config.security_auth_cookie_name)

    return _logout


@pytest.fixture
async def login(config, test_client, logout, register_test_user) -> Callable:
    async def _login(*, user: dict | None = None, **kwargs) -> dict:
        await logout()
        if not user:
            user = await register_test_user(**kwargs)
        resp = await test_client.post(
            "/auth/cookie/login",
            data={"username": user["email"], "password": user["password"]},
        )
        if resp.status_code != 204:
            raise Exception(
                f"Failed to login (got status {resp.status_code}: {resp.text})"
            )
        if not resp.cookies.get(config.security_auth_cookie_name):
            raise Exception("No cookies retrieved after login")
        return user

    return _login


@pytest.fixture(scope="session")
def status_fail_msg() -> Callable:
    def _status_fail_msg(expected_status: int, response: Response) -> tuple[bool, str]:
        return (
            f"HTTP {response.status_code} (expected: {expected_status})"
            f" -- {response.text}"
        )

    return _status_fail_msg


# @pytest.fixture(autouse=True)
# def disable_network_calls(monkeypatch):
#     """Prevents outside network access while testing"""

#     def stunted_get():
#         raise RuntimeError("Network access not allowed during testing!")

#     monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
