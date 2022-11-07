import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_uidata(config, test_client: AsyncClient):
    endpoint = f"{config.root_path}/admin"
    response = await test_client.get(endpoint)
    assert response.status_code == 200, f"Response of {endpoint} != 200"
    assert response.json()["message"]
