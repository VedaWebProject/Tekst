import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_api_status(
    test_client: AsyncClient,
    assert_status,
):
    resp = await test_client.get("/status")
    assert_status(200, resp)
    assert isinstance(resp.json(), dict)
    assert "status" in resp.json()
