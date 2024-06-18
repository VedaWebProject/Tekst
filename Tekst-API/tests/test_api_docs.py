import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_root_redirect_to_docs(config, test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get("/")
    assert resp.status_code == 307, status_fail_msg(307, resp)


@pytest.mark.anyio
async def test_load_openapi_schema(config, test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get(config.api_doc.openapi_url)
    assert resp.status_code == 200, status_fail_msg(200, resp)


@pytest.mark.anyio
async def test_load_swaggerui(config, test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get(config.api_doc.swaggerui_url)
    assert resp.status_code == 200, status_fail_msg(200, resp)


@pytest.mark.anyio
async def test_load_redoc(config, test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get(config.api_doc.redoc_url)
    assert resp.status_code == 200, status_fail_msg(200, resp)
