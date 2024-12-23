import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_root_redirect_to_docs(
    config,
    test_client: AsyncClient,
    assert_status,
):
    resp = await test_client.get("/")
    assert_status(307, resp)


@pytest.mark.anyio
async def test_load_openapi_schema(
    config,
    test_client: AsyncClient,
    assert_status,
):
    resp = await test_client.get(config.api_doc.openapi_url)
    assert_status(200, resp)


@pytest.mark.anyio
async def test_load_swaggerui(
    config,
    test_client: AsyncClient,
    assert_status,
):
    resp = await test_client.get(config.api_doc.swaggerui_url)
    assert_status(200, resp)


@pytest.mark.anyio
async def test_load_redoc(
    config,
    test_client: AsyncClient,
    assert_status,
):
    resp = await test_client.get(config.api_doc.redoc_url)
    assert_status(200, resp)
