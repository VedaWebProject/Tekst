import pytest

from httpx import AsyncClient, Response


def _assert_search_resp(
    resp: Response,
    *,
    expected_hits: int,
    expected_status: int = 200,
) -> None:
    assert resp.status_code == expected_status
    assert isinstance(resp.json(), dict)
    assert "hits" in resp.json()
    assert "totalHits" in resp.json()
    assert resp.json()["totalHits"] == expected_hits


@pytest.mark.anyio
async def test_admin_create_search_index(
    test_client: AsyncClient,
    insert_test_data,
    assert_status,
    login,
    wait_for_task_success,
):
    await insert_test_data()
    await login(is_superuser=True)

    # create task to create index
    resp = await test_client.get("/search/index/create")
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])

    # get index info
    resp = await test_client.get("/search/index/info")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2


@pytest.mark.anyio
async def test_get_indices_info(
    test_client: AsyncClient,
    use_indices,
    assert_status,
    login,
):
    await login(is_superuser=True)
    resp = await test_client.get("/search/index/info")
    assert_status(200, resp)
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 2
    assert resp.json()[0]["upToDate"]


@pytest.mark.anyio
async def test_quick(
    test_client: AsyncClient,
    use_indices,
    assert_status,
):
    # find everything
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "*",
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        expected_hits=19,
    )

    # simple without wildcards or regexes
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "jäger",
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
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
        expected_hits=0,
    )

    # wildcards
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "mau*",
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        expected_hits=2,
    )

    # phrase
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": '"mit der"',
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        expected_hits=2,
    )

    # phrase slop
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": '"you the"~6',
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        expected_hits=3,
    )

    # fuzzy
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "maus~",
                "qck": {"op": "OR", "re": False, "txt": []},
            },
        ),
        expected_hits=6,
    )

    # regex
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "mau.*",
                "qck": {"op": "OR", "re": True, "txt": []},
            },
        ),
        expected_hits=2,
    )

    # wildcards on specific text
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "s*",
                "qck": {"op": "OR", "re": False, "txt": ["654b825533ee5737b297f8e3"]},
            },
        ),
        expected_hits=9,
    )

    # request too many results
    resp = await test_client.post(
        "/search",
        json={
            "type": "quick",
            "q": "s*",
            "gen": {
                "pgn": {"pg": 1, "pgs": 10001},
                "sort": "relevance",
                "strict": False,
            },
            "qck": {"op": "OR", "re": False, "txt": []},
        },
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_advanced_text_annotation(
    test_client: AsyncClient,
    use_indices,
):
    # token empty, nothing else (finds everything)
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6656cc7b81a66322c1bffb24", "occ": "should"},
                        # this counts as "empty"
                        "rts": {"type": "textAnnotation", "token": "    *        "},
                    }
                ],
            },
        ),
        expected_hits=12,
    )

    # search for location comment
    # (to test custom highlights generator of text annotation resource type)
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {
                            "res": "6656cc7b81a66322c1bffb24",
                            "occ": "should",
                            "cmt": "m*",
                        },
                        "rts": {"type": "textAnnotation", "anno": []},
                    }
                ],
            },
        ),
        expected_hits=1,
    )

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
            },
        ),
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
            },
        ),
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
            },
        ),
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
            },
        ),
        expected_hits=7,
    )

    # special "comment" annotation
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
                            "anno": [
                                {
                                    "k": "comment",
                                    "v": "thi*",
                                    "wc": True,
                                }
                            ],
                        },
                    }
                ],
            },
        ),
        expected_hits=1,
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
            },
        ),
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
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_plain_text(
    test_client: AsyncClient,
    use_indices,
):
    # text, simple term, optional/should
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
            },
        ),
        expected_hits=1,
    )

    # text, simple term, required/must
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "654b825533ee5737b297f8f3", "occ": "must"},
                        "rts": {"type": "plainText", "text": "gans"},
                    }
                ],
            },
        ),
        expected_hits=1,
    )

    # text, simple term, exclude/not
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "654b825533ee5737b297f8f3", "occ": "not"},
                        "rts": {"type": "plainText", "text": "gans"},
                    }
                ],
            },
        ),
        expected_hits=18,
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
            },
        ),
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
            },
        ),
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
            },
        ),
        expected_hits=0,
    )

    # search in location comment field
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {
                            "res": "66471b68ba9e65342c8e495b",
                            "occ": "should",
                            "cmt": "s*",
                        },
                        "rts": {"type": "plainText"},
                    }
                ],
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_images(
    test_client: AsyncClient,
    use_indices,
):
    # caption, empty
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6641ce24affa6cb96bc85a55", "occ": "should"},
                        "rts": {"type": "images", "caption": "*"},
                    }
                ],
            },
        ),
        expected_hits=1,
    )
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
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_audio(
    test_client: AsyncClient,
    use_indices,
):
    # caption, empty
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "6641d510affa6cb96bc85a5b", "occ": "should"},
                        "rts": {"type": "audio", "caption": "*"},
                    }
                ],
            },
        ),
        expected_hits=1,
    )

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
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_external_references(
    test_client: AsyncClient,
    use_indices,
):
    # description, empty
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "66471de0ba9e65342c8e4995", "occ": "should"},
                        "rts": {"type": "externalReferences", "text": "*"},
                    }
                ],
            },
        ),
        expected_hits=1,
    )

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
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_rich_text(
    test_client: AsyncClient,
    use_indices,
):
    # html, empty query
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67472c393d0d7622956981c9", "occ": "should"},
                        "rts": {"type": "richText", "html": "*   "},
                    }
                ],
            },
        ),
        expected_hits=1,
    )

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
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_export_search_results(
    test_client: AsyncClient,
    use_indices,
    assert_status,
    wait_for_task_success,
):
    resp = await test_client.post(
        "/search/export",
        json={
            "type": "quick",
            "q": "*",
            "gen": {
                "sort": "relevance",
                "strict": False,
            },
            "qck": {"op": "OR", "re": False, "txt": []},
        },
    )
    assert_status(202, resp)
    assert "id" in resp.json()
    assert await wait_for_task_success(resp.json()["id"])
