import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_load_openapi_schema(
    config, api_path, test_client: AsyncClient, status_fail_msg
):
    resp = await test_client.get(config.doc_openapi_url)
    assert resp.status_code == 200, status_fail_msg(200, resp)


@pytest.mark.anyio
async def test_load_swaggerui(
    config, api_path, test_client: AsyncClient, status_fail_msg
):
    resp = await test_client.get(config.doc_swaggerui_url)
    assert resp.status_code == 200, status_fail_msg(200, resp)


@pytest.mark.anyio
async def test_load_redoc(config, api_path, test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get(config.doc_redoc_url)
    assert resp.status_code == 200, status_fail_msg(200, resp)
