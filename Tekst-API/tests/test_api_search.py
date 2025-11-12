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
    login,
    use_indices,
    assert_status,
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
    # find everything, default settings
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "*",
            },
        ),
        expected_hits=8,
    )

    # simple without wildcards or regexes, default settings
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "foo",
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
                "q": "foö",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": True,
                },
            },
        ),
        expected_hits=1,
    )

    # simple without wildcards or regexes, strict, no diacritics
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "foo",
                "gen": {
                    "pgn": {"pg": 1, "pgs": 10},
                    "sort": "relevance",
                    "strict": True,
                },
            },
        ),
        expected_hits=2,
    )

    # wildcards
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "b*",
            },
        ),
        expected_hits=4,
    )

    # phrase
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": '"foo foo"',
            },
        ),
        expected_hits=1,
    )

    # phrase slop
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": '"foö word"~6',
            },
        ),
        expected_hits=1,
    )

    # fuzzy
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "fuo~",
            },
        ),
        expected_hits=4,
    )

    # regex
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "b.*",
                "qck": {"re": True},
            },
        ),
        expected_hits=4,
    )

    # wildcards on specific text
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "b*",
                "qck": {"txt": ["67c03aed5dbf06b9624fd57e"]},
            },
        ),
        expected_hits=2,
    )

    # include inherited higher-level contents
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "*",
                "qck": {"inh": True},
            },
        ),
        expected_hits=8,
    )

    # find locations on all levels
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "quick",
                "q": "*",
                "qck": {"allLvls": True},
            },
        ),
        expected_hits=8,
    )

    # request too many results
    resp = await test_client.post(
        "/search",
        json={
            "type": "quick",
            "q": "f*",
            "gen": {
                "pgn": {"pg": 1, "pgs": 10001},
                "sort": "relevance",
                "strict": False,
            },
        },
    )
    assert_status(400, resp)


@pytest.mark.anyio
async def test_advanced_text_annotation(
    test_client: AsyncClient,
    use_indices,
):
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
                            "res": "67c0442e906e79b9062e22f6",
                            "occ": "should",
                            "cmt": "this",
                        },
                        "rts": {"type": "textAnnotation", "anno": []},
                    }
                ],
            },
        ),
        expected_hits=1,
    )

    # token form anno
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "form", "v": "foo"}],
                        },
                    }
                ],
            },
        ),
        expected_hits=1,
    )

    # token form anno (value list)
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "form", "v": ["foo"]}],
                        },
                    }
                ],
            },
        ),
        expected_hits=1,
    )

    # token form anno (value list, no hits!)
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "form", "v": ["foo", "bar"]}],
                        },
                    }
                ],
            },
        ),
        expected_hits=0,
    )

    # token form anno, with wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "form", "v": "b*", "wc": True}],
                        },
                    }
                ],
            },
        ),
        expected_hits=2,
    )

    # annotation key only (key exists)
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "type", "v": ""}],
                        },
                    }
                ],
            },
        ),
        expected_hits=4,
    )

    # annotation key only, explicitly set to "exists"
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [
                                {
                                    "k": "type",
                                    "v": "doesn't matter!",
                                    "spc": "exists",
                                }
                            ],
                        },
                    }
                ],
            },
        ),
        expected_hits=4,
    )

    # annotation key missing
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [
                                {
                                    "k": "comment",
                                    "v": "doesn't matter!",
                                    "spc": "missing",
                                }
                            ],
                        },
                    }
                ],
            },
        ),
        expected_hits=3,
    )

    # annotation key and value
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "type", "v": "token"}],
                        },
                    }
                ],
            },
        ),
        expected_hits=4,
    )

    # special "comment" annotation
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
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
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [{"k": "type", "v": "t*", "wc": True}],
                        },
                    }
                ],
            },
        ),
        expected_hits=4,
    )

    # token, annotation key and value
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0442e906e79b9062e22f6", "occ": "should"},
                        "rts": {
                            "type": "textAnnotation",
                            "anno": [
                                {"k": "form", "v": "foo"},
                                {"k": "type", "v": "token"},
                            ],
                        },
                    }
                ],
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_location_metadata(
    test_client: AsyncClient,
    use_indices,
):
    # search for key and value
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c04473906e79b9062e22fb", "occ": "should"},
                        "rts": {
                            "type": "locationMetadata",
                            "entries": [{"k": "word", "v": "foo"}],
                        },
                    }
                ],
            },
        ),
        expected_hits=1,
    )

    # search for key and value with wildcards
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c04473906e79b9062e22fb", "occ": "should"},
                        "rts": {
                            "type": "locationMetadata",
                            "entries": [{"k": "word", "v": "b*", "wc": True}],
                        },
                    }
                ],
            },
        ),
        expected_hits=2,
    )

    # search for key only
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c04473906e79b9062e22fb", "occ": "should"},
                        "rts": {
                            "type": "locationMetadata",
                            "entries": [{"k": "word"}],
                        },
                    }
                ],
            },
        ),
        expected_hits=4,
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
                        "cmn": {"res": "67c043c0906e79b9062e22f4", "occ": "should"},
                        "rts": {
                            "type": "plainText",
                            # this also tests the search replacement config as "o"
                            # is replaced by "a" and the original text is "Foö"
                            "text": "faö",
                        },
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
                        "cmn": {"res": "67c043c0906e79b9062e22f4", "occ": "must"},
                        "rts": {"type": "plainText", "text": "bar"},
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
                        "cmn": {"res": "67c043c0906e79b9062e22f4", "occ": "not"},
                        "rts": {"type": "plainText", "text": "bar"},
                    }
                ],
            },
        ),
        expected_hits=11,
    )

    # text with wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c043c0906e79b9062e22f4", "occ": "should"},
                        "rts": {"type": "plainText", "text": "b*"},
                    }
                ],
            },
        ),
        expected_hits=2,
    )

    # text, simple term, strict, correct diacritics
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c043c0906e79b9062e22f4", "occ": "should"},
                        "rts": {"type": "plainText", "text": "faö"},
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
                        "cmn": {"res": "67c043c0906e79b9062e22f4", "occ": "should"},
                        "rts": {"type": "plainText", "text": "fao"},
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
                            "res": "67c043c0906e79b9062e22f4",
                            "occ": "should",
                            "cmt": "com*",
                        },
                        "rts": {"type": "plainText"},
                    }
                ],
            },
        ),
        expected_hits=3,
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
                        "cmn": {"res": "67c0444e906e79b9062e22f8", "occ": "should"},
                        "rts": {"type": "images", "caption": "*"},
                    }
                ],
            },
        ),
        expected_hits=4,
    )
    # caption, wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0444e906e79b9062e22f8", "occ": "should"},
                        "rts": {"type": "images", "caption": "b*"},
                    }
                ],
            },
        ),
        expected_hits=2,
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
                        "cmn": {"res": "67c04445906e79b9062e22f7", "occ": "should"},
                        "rts": {"type": "audio", "caption": "*"},
                    }
                ],
            },
        ),
        expected_hits=4,
    )

    # caption, wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c04445906e79b9062e22f7", "occ": "should"},
                        "rts": {"type": "audio", "caption": "f*"},
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
                        "cmn": {"res": "67c0445b906e79b9062e22f9", "occ": "should"},
                        "rts": {"type": "externalReferences", "text": "*"},
                    }
                ],
            },
        ),
        expected_hits=4,
    )

    # description, wildcard
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c0445b906e79b9062e22f9", "occ": "should"},
                        "rts": {"type": "externalReferences", "text": "b*"},
                    }
                ],
            },
        ),
        expected_hits=2,
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
                        "cmn": {"res": "67c04415906e79b9062e22f5", "occ": "should"},
                        "rts": {"type": "richText", "html": "*   "},
                    }
                ],
            },
        ),
        expected_hits=4,
    )

    # phrase
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c04415906e79b9062e22f5", "occ": "should"},
                        "rts": {"type": "richText", "html": '"foo foo"'},
                    }
                ],
            },
        ),
        expected_hits=1,
    )


@pytest.mark.anyio
async def test_advanced_location_range(
    test_client: AsyncClient,
    use_indices,
):
    # text, simple term, should/optional, with location range
    _assert_search_resp(
        await test_client.post(
            "/search",
            json={
                "type": "advanced",
                "q": [
                    {
                        "cmn": {"res": "67c043c0906e79b9062e22f4", "occ": "should"},
                        "rts": {"type": "plainText", "text": "b*"},
                    }
                ],
                "adv": {
                    "rng": {
                        "lvl": 1,
                        "from": 0,
                        "to": 1,
                    }
                },
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
