import pytest

from httpx import AsyncClient


@pytest.mark.anyio
async def test_quick_search_simple(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # simple without wildcards or regexes
    search_req_body = {
        "type": "quick",
        "q": "maus",
        "gen": {"pgn": {"pg": 1, "pgs": 10}, "sort": "relevance", "strict": False},
        "qck": {"op": "OR", "re": False, "txt": []},
    }
    resp = await test_client.post("/search", json=search_req_body)
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "hits" in resp.json()
    assert "totalHits" in resp.json()
    assert resp.json()["totalHits"] == 1


@pytest.mark.anyio
async def test_quick_search_wildcards(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # wildcards
    search_req_body = {
        "type": "quick",
        "q": "mau*",
        "gen": {"pgn": {"pg": 1, "pgs": 10}, "sort": "relevance", "strict": False},
        "qck": {"op": "OR", "re": False, "txt": []},
    }
    resp = await test_client.post("/search", json=search_req_body)
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "hits" in resp.json()
    assert "totalHits" in resp.json()
    assert resp.json()["totalHits"] == 1


@pytest.mark.anyio
async def test_quick_search_regex(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # regex
    search_req_body = {
        "type": "quick",
        "q": "mau.*",
        "gen": {"pgn": {"pg": 1, "pgs": 10}, "sort": "relevance", "strict": False},
        "qck": {"op": "OR", "re": True, "txt": []},
    }
    resp = await test_client.post("/search", json=search_req_body)
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "hits" in resp.json()
    assert "totalHits" in resp.json()
    assert resp.json()["totalHits"] == 1


@pytest.mark.anyio
async def test_quick_search_specific_text(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # wildcards on specific text
    search_req_body = {
        "type": "quick",
        "q": "s*",
        "gen": {"pgn": {"pg": 1, "pgs": 10}, "sort": "relevance", "strict": False},
        "qck": {"op": "OR", "re": False, "txt": ["654b825533ee5737b297f8e3"]},
    }
    resp = await test_client.post("/search", json=search_req_body)
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), dict)
    assert "hits" in resp.json()
    assert "totalHits" in resp.json()
    assert resp.json()["totalHits"] == 9
