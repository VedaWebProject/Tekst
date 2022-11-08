# import pytest
# from httpx import AsyncClient


# @pytest.mark.anyio
# async def test_create_node(root_path, test_client: AsyncClient):
#     endpoint = f"{root_path}/nodes"
#     payload = {}  # TODO ...
#     resp = await test_client.post(endpoint, json=payload)
#     assert resp.status_code == 201, f"response status {resp.status_code} != 201"
#     # TODO ...
