import pytest

from httpx import AsyncClient
from textrig import pkg_meta


@pytest.mark.anyio
async def test_platform_data(api_path, test_client: AsyncClient, status_fail_msg):
    endpoint = f"{api_path}/platform"
    resp = await test_client.get(endpoint)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert resp.json()["textrigInfo"]["version"] == pkg_meta["version"]
