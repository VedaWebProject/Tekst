import asyncio

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

from asgi_lifespan import LifespanManager
from beanie import PydanticObjectId
from bson import ObjectId, json_util
from elasticsearch import Elasticsearch
from fastapi import Response
from httpx import ASGITransport, AsyncClient
from humps import camelize
from tekst import db, tasks
from tekst.app import app
from tekst.auth import _create_user
from tekst.config import TekstConfig, get_config
from tekst.models.user import UserCreate
from tekst.search import create_indices_task
from tekst.search.templates import IDX_ALIAS


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
    """Returns a function to get the path to a file relative to tests/data"""

    def _get_sample_data_path(rel_path: str) -> Path:
        return Path(request.config.rootdir) / "tekst/sample_data" / rel_path

    return _get_sample_data_path


@pytest.fixture
def get_sample_data(get_sample_data_path) -> Callable[[str], Any]:
    """
    Returns a function to get the object representation
    of a JSON file relative to tests/data
    """

    def _get_sample_data(
        rel_path: str,
        for_http: bool = False,
    ) -> Any:
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


@pytest.fixture(scope="session")
async def db_client_override(config) -> db.DatabaseClient:
    """Dependency override for the database client dependency"""
    db_client = db.DatabaseClient(config.db.uri)
    yield db_client
    # close db connection
    db_client.close()


@pytest.fixture(scope="session")
async def database(
    config,
    db_client_override,
) -> db.Database:
    """DB driver for test session"""
    yield db_client_override[config.db.name]


@pytest.fixture(scope="session")
async def test_app(
    config,
    db_client_override,
):
    """Provides an app instance with overridden dependencies"""
    app.dependency_overrides[db.get_db_client] = lambda: db_client_override
    async with LifespanManager(app):
        yield app
    # cleanup data
    await db_client_override.drop_database(config.db.name)


@pytest.fixture
async def test_client(
    test_app,
    config,
) -> AsyncClient:
    """Returns an asynchronous test client for API testing"""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url=f"{config.server_url}{config.api_path}",
    ) as client:
        # set XSRF header and cookie if server sends XSRF cookie
        resp = await client.get("/")
        xsrf_token = resp.cookies.get("XSRF-TOKEN")
        if xsrf_token:
            client.headers.setdefault("X-XSRF-TOKEN", xsrf_token)
            client.cookies.setdefault("XSRF-TOKEN", xsrf_token)
        # yield client instance
        yield client


@pytest.fixture
async def insert_sample_data(
    database,
    get_sample_data,
) -> Callable:
    """
    Returns an asynchronous function to insert
    test data into their respective database collections
    """

    async def _insert_sample_data(*collections: str) -> dict[str, list[str]]:
        ids = dict()
        collections = collections or [
            "contents",
            "locations",
            "resources",
            "state",
            "texts",
            "users",
        ]
        for collection in collections:
            sample_data = get_sample_data(f"db/{collection}.json")
            if not sample_data:
                raise Exception(
                    f"Could not find sample data for collection '{collection}'"
                )
            result = await database[collection].insert_many(sample_data)
            if not result.acknowledged:
                raise Exception(f"Failed to insert into test collection '{collection}'")
            ids[collection] = [str(id_) for id_ in result.inserted_ids]
        return ids

    return _insert_sample_data


@pytest.fixture
async def use_indices(
    config,
    insert_sample_data,
) -> Iterator[None]:
    await insert_sample_data()
    await create_indices_task(force=True)
    yield
    for index in Elasticsearch(config.es.uri).indices.get(index=IDX_ALIAS).body:
        Elasticsearch(config.es.uri).indices.delete(index=index)


@pytest.fixture
def get_mock_user() -> Callable:
    def _get_mock_user(suffix: str = ""):
        return dict(
            email=f"user{suffix}@foo.de",
            username=f"user{suffix}",
            password="poiPOI098",
            name="Foo Bar",
            affiliation="Some Institution",
        )

    return _get_mock_user


@pytest.fixture(autouse=True)
async def setup_teardown(database) -> Callable:
    yield
    # drop all DB collections
    for collection in await database.list_collection_names():
        await database.drop_collection(collection)


@pytest.fixture
async def register_test_user(get_mock_user) -> Callable:
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
        user_data = get_mock_user(suffix=suffix)
        user = UserCreate(**user_data)
        user.is_active = is_active
        user.is_verified = is_verified
        user.is_superuser = is_superuser
        created_user = await _create_user(user)
        return {"id": str(created_user.id), **user_data}

    return _register_test_user


@pytest.fixture
async def logout(
    config,
    test_client: AsyncClient,
) -> Callable:
    async def _logout() -> None:
        await test_client.post("/auth/cookie/logout")
        test_client.cookies.delete(name=config.security.auth_cookie_name)

    return _logout


@pytest.fixture
async def login(
    config,
    test_client,
    logout,
    register_test_user,
) -> Callable:
    async def _login(
        user: dict | None = None,
        **kwargs,
    ) -> dict:
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
        if not resp.cookies.get(config.security.auth_cookie_name):
            raise Exception("No cookies retrieved after login")
        return user

    return _login


@pytest.fixture(scope="session")
def assert_status() -> Callable:
    def _assert_status(
        expected_status: int,
        resp: Response,
    ) -> None:
        assert (
            resp.status_code == expected_status
        ), f"HTTP {resp.status_code} -- {resp.text}"

    return _assert_status


@pytest.fixture(scope="session")
def wait_for_task_success():
    async def _wait_for_task_success(
        task_id: str,
        tries: int = 10,
        interval_s: int = 1,
    ) -> bool:
        for _ in range(tries):
            task = await tasks.TaskDocument.get(PydanticObjectId(task_id))
            if task:
                if task.status == "done":
                    return True
                elif task.status == "failed":
                    print(f"TASK FAILED: {str(task)}")
                    return False
            await asyncio.sleep(interval_s)
        if task:
            return False
        else:
            raise Exception(f"Task {task_id} not found")

    return _wait_for_task_success
