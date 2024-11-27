from collections.abc import Callable

import pytest

from httpx import AsyncClient, Response


def _assert_search_resp(
    resp: Response,
    status_assertion: Callable,
    expected_status: int,
    expected_hits: int,
) -> None:
    assert status_assertion(expected_status, resp)
    assert isinstance(resp.json(), dict)
    assert "hits" in resp.json()
    assert "totalHits" in resp.json()
    assert resp.json()["totalHits"] == expected_hits


@pytest.mark.anyio
async def test_get_indices_info(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
    login,
):
    await login(is_superuser=True)
    resp = await test_client.get("/search/index/info")
    assert status_assertion(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2
    assert resp.json()[0]["upToDate"]


@pytest.mark.anyio
async def test_quick(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # simple without wildcards or regexes
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "jäger",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=2,
    )

    # simple without wildcards or regexes, strict, correct diacritics
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "jäger",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": True,
                },
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=2,
    )

    # simple without wildcards or regexes, strict, wrong diacritics
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "jager",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": True,
                },
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=0,
    )

    # wildcards
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "mau*",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=2,
    )

    # phrase
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": '"mit der"',
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=2,
    )

    # phrase slop
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": '"you the"~6',
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=3,
    )

    # fuzzy
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "maus~",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=6,
    )

    # regex
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "mau.*",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "qck": {"op": "OR", "re": True, "txt": []},
            },
        ),
        status_assertion,
        200,
        expected_hits=2,
    )

    # wildcards on specific text
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "s*",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "qck": {"op": "OR", "re": False, "txt": ["654b825533ee5737b297f8e3"]},
            },
        ),
        status_assertion,
        200,
        expected_hits=9,
    )


@pytest.mark.anyio
async def test_advanced_text_annotation(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # token only
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6656cc7b81a66322c1bffb24", "occ": "should"},
                        "rts": {"type": "textAnnotation", "token": "fuchs"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )

    # token only, with wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6656cc7b81a66322c1bffb24", "occ": "should"},
                        "rts": {"type": "textAnnotation", "token": "f*", "twc": True},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=4,
    )

    # annotation key only (key exists)
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6656cc7b81a66322c1bffb24", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "Entity", "v": ""}],
                        },
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=10,
    )

    # annotation key and value
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6656cc7b81a66322c1bffb24", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "Entity", "v": "fox"}],
                        },
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=7,
    )

    # annotation key and value with wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6656cc7b81a66322c1bffb24", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "Entity", "v": "f*", "wc": True}],
                        },
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=7,
    )

    # token, annotation key and value
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6656cc7b81a66322c1bffb24", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "token": "fuchs",
                            "anno": [{"k": "Entity", "v": "Fox"}],
                        },
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_plain_text(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # text, simple term
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "654b825533ee5737b297f8f3", "occ": "should"},
                        "rts": {"type": "plainText", "text": "gans"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )

    # text with wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "654b825533ee5737b297f8f3", "occ": "should"},
                        "rts": {"type": "plainText", "text": "g*"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=4,
    )

    # text, simple term, strict, correct diacritics
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "654b825533ee5737b297f8f3", "occ": "should"},
                        "rts": {"type": "plainText", "text": "jäger"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": True,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )

    # text, simple term, strict, wrong diacritics
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "654b825533ee5737b297f8f3", "occ": "should"},
                        "rts": {"type": "plainText", "text": "jager"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": True,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=0,
    )


@pytest.mark.anyio
async def test_advanced_images(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # caption, wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6641ce24affa6cb96bc85a55", "occ": "should"},
                        "rts": {"type": "images", "caption": "musikalisch*"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_audio(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # caption, wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6641d510affa6cb96bc85a5b", "occ": "should"},
                        "rts": {"type": "audio", "caption": "g*"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_external_resources(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # description, wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "66471de0ba9e65342c8e4995", "occ": "should"},
                        "rts": {"type": "externalReferences", "text": "kurzfilm*"},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_rich_text(
    test_client: AsyncClient,
    use_indices,
    status_assertion,
):
    # phrase
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67472c393d0d7622956981c9", "occ": "should"},
                        "rts": {"type": "richText", "html": '"c g c g"'},
                    }
                ],
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": False,
                },
                "adv": {},
            },
        ),
        status_assertion,
        200,
        expected_hits=1,
    )
