import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_api_status(
    test_client: AsyncClient,
    status_assertion,
):
    resp = await test_client.get("/status")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "status" in resp.json()
