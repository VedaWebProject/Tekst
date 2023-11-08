import pytest

from httpx import AsyncClient
from tekst import pkg_meta


@pytest.mark.anyio
async def test_platform_data(api_path, test_client: AsyncClient, status_fail_msg):
    resp = await test_client.get("/platform")
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["tekst"]["version"] == pkg_meta["version"]
