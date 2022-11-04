import pytest
from httpx import AsyncClient
from textrig import pkg_meta


@pytest.mark.anyio
async def test_uidata(config, test_client: AsyncClient):
    endpoint = f"{config.root_path}/uidata"
    response = await test_client.get(endpoint)
    assert response.status_code == 200, f"Response of {endpoint} != 200"
    assert response.json()["platform"]["version"] == pkg_meta["version"]
