import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_root_redirect_to_docs(
    config, test_client: AsyncClient, status_assertion
):
    resp = await test_client.get("/")
    assert status_assertion(307, resp)


@pytest.mark.anyio
async def test_load_openapi_schema(config, test_client: AsyncClient, status_assertion):
    resp = await test_client.get(config.api_doc.openapi_url)
    assert status_assertion(200, resp)


@pytest.mark.anyio
async def test_load_swaggerui(config, test_client: AsyncClient, status_assertion):
    resp = await test_client.get(config.api_doc.swaggerui_url)
    assert status_assertion(200, resp)


@pytest.mark.anyio
async def test_load_redoc(config, test_client: AsyncClient, status_assertion):
    resp = await test_client.get(config.api_doc.redoc_url)
    assert status_assertion(200, resp)
