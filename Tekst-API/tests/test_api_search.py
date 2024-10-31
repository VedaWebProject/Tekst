import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_quick_search(
    test_client: AsyncClient,
    create_indices,
    status_fail_msg,
):
    search_req_body = {
        "type": "quick",
        "q": "maus",
        "gen": {"pgn": {"pg": 1, "pgs": 10}, "sort": "relevance", "strict": False},
        "qck": {"op": "OR", "re": False, "txt": []},
    }
    resp = await test_client.post("/search", json=search_req_body)
    assert resp.status_code == 200, status_fail_msg(200, resp)
    assert isinstance(resp.json(), dict)
    assert "hits" in resp.json()
    assert "totalHits" in resp.json()
    assert resp.json()["totalHits"] == 1
