# import pytest
# from httpx import AsyncClient


# @pytest.mark.anyio
# async def test_uidata(root_path, test_client: AsyncClient):
#     endpoint = f"{root_path}/admin"
#     resp = await test_client.get(endpoint)
#     assert resp.status_code == 200, f"HTTP {resp.status_code} != 200 ({resp.json()})"
#     assert resp.json()["message"]
