from importlib import import_module

import pytest

from tekst.resources import resource_types_mgr


def _migration_fn(migration_name):
    return import_module(f"tekst.db.migrations.migration_{migration_name}").migration


@pytest.mark.anyio
async def test_0_1_0a0(database):
    await _migration_fn("0_1_0a0")(database)  # no-op


@pytest.mark.anyio
async def test_0_2_0a0(database):
    await database.state.insert_one({"custom_fonts": ["foo", "bar"]})
    await _migration_fn("0_2_0a0")(database)
    state = await database.state.find_one({})
    assert "fonts" in state
    assert "custom_fonts" not in state
    assert state.get("fonts")[1] == "bar"


@pytest.mark.anyio
async def test_0_2_1a0(database):
    await database.state.insert_one({"register_intro_text": ["foo", "bar"]})
    await _migration_fn("0_2_1a0")(database)
    state = await database.state.find_one({})
    assert "register_intro_text" not in state
    assert len(state.keys()) == 1
    assert "_id" in state


@pytest.mark.anyio
async def test_0_3_0a0(
    database,
    get_test_data,
):
    data = get_test_data("migrations/0_3_0a0.json")
    for coll_name in data:
        await database[coll_name].insert_many(data[coll_name])

    # run migration
    await _migration_fn("0_3_0a0")(database)

    # assert the data has been fixed by the migration
    correction = await database.corrections.find_one({})
    assert correction
    assert "location_id" in correction
    assert str(correction["location_id"]) == "654b825533ee5737b297f8e5"
    assert not await database.precomputed.find_one({"precomputed_type": "coverage"})


@pytest.mark.anyio
async def test_0_4_0a0(
    database,
    get_test_data,
):
    res = get_test_data("migrations/0_4_0a0.json")
    res_id = (await database.resources.insert_one(res)).inserted_id
    assert res_id

    # run migration
    await _migration_fn("0_4_0a0")(database)
    res = await database.resources.find_one({"_id": res_id})

    # assert the data has been fixed by the migration
    assert "config" in res
    assert "deeplLinks" not in res["config"]
    assert "plainText" in res["config"]
    assert "deeplLinks" in res["config"]["plainText"]


@pytest.mark.anyio
async def test_0_4_1a0(database, get_test_data):
    res = get_test_data("migrations/0_4_1a0.json")
    res_id = (await database.resources.insert_one(res)).inserted_id
    assert res_id

    # run migration
    await _migration_fn("0_4_1a0")(database)
    res = await database.resources.find_one({"_id": res_id})

    # assert the data has been fixed by the migration
    assert "config" in res
    assert "plainText" not in res["config"]
    assert "plain_text" in res["config"]
    assert "deepl_links" in res["config"]["plain_text"]
    assert "source_language" in res["config"]["plain_text"]["deepl_links"]


@pytest.mark.anyio
async def test_0_4_2a0(database, get_test_data):
    content = get_test_data("migrations/0_4_2a0.json")
    content_id = (await database.contents.insert_one(content)).inserted_id
    assert content_id

    # run migration
    await _migration_fn("0_4_2a0")(database)
    content = await database.contents.find_one({"_id": content_id})

    # assert the data has been fixed by the migration
    assert "extra" not in content
    assert "transform_context" in content


@pytest.mark.anyio
async def test_0_5_0a0(database, get_test_data):
    res = get_test_data("migrations/0_5_0a0.json")
    conf_val = res["config"]["common"]["show_on_parent_level"]
    assert conf_val is not None
    res_id = (await database.resources.insert_one(res)).inserted_id
    assert res_id

    # run migration
    await _migration_fn("0_5_0a0")(database)
    res = await database.resources.find_one({"_id": res_id})

    # assert the data has been fixed by the migration
    assert "config" in res
    assert "common" in res["config"]
    assert "show_on_parent_level" not in res["config"]["common"]
    assert "enable_content_context" in res["config"]["common"]
    assert res["config"]["common"]["enable_content_context"] == conf_val


@pytest.mark.anyio
async def test_0_6_0a0(database, get_test_data):
    state = get_test_data("migrations/0_6_0a0.json")
    await database.state.insert_one(state)

    # run migration
    await _migration_fn("0_6_0a0")(database)
    state = await database.state.find_one({})

    # assert the data has been fixed by the migration
    assert "always_show_text_info" not in state


@pytest.mark.anyio
async def test_0_7_0a0(database, get_test_data):
    msg = get_test_data("migrations/0_7_0a0.json")
    await database.messages.insert_one(msg)

    # run migration
    await _migration_fn("0_7_0a0")(database)
    msg = await database.messages.find_one({})

    # assert the data has been fixed by the migration
    assert "time" not in msg
    assert "created_at" in msg


@pytest.mark.anyio
async def test_0_8_0a0(database, get_test_data):
    footer_segment = get_test_data("migrations/0_8_0a0.json")
    await database.segments.insert_one(footer_segment)

    # run migration
    await _migration_fn("0_8_0a0")(database)
    footer_segment = await database.segments.find_one({})

    # assert the data has been fixed by the migration
    assert "key" in footer_segment
    assert footer_segment["key"] == "systemFooterUpper"


@pytest.mark.anyio
async def test_0_9_0a0(
    database,
    get_test_data,
):
    resources = get_test_data("migrations/0_9_0a0.json")
    await database.resources.insert_many(resources)

    # run migration
    await _migration_fn("0_9_0a0")(database)
    resources = await database.resources.find({"resource_type": "plainText"}).to_list()

    # assert the data has been fixed by the migration
    assert len(resources) > 0
    for res in resources:
        assert "reduced_view" not in res["config"]["general"]
        assert "focus_view" in res["config"]["general"]
        assert "single_line" in res["config"]["general"]["focus_view"]
        assert "single_line_delimiter" not in res["config"]["general"]["focus_view"]
        assert "delimiter" in res["config"]["general"]["focus_view"]


@pytest.mark.anyio
async def test_0_10_0a0(
    database,
    get_test_data,
):
    resources = get_test_data("migrations/0_10_0a0.json")
    await database.resources.insert_many(resources)

    # run migration
    await _migration_fn("0_10_0a0")(database)
    resources = await database.resources.find({}).to_list()

    # assert the data has been fixed by the migration
    assert len(resources) > 0
    for res in resources:
        assert "comment" not in res
        assert "subtitle" in res
        assert res["subtitle"][0]["translation"] == "DESCRIPTION"
        assert "description" in res
        assert res["description"][0]["translation"] == "COMMENT"


@pytest.mark.anyio
async def test_0_11_0a0(
    database,
    get_test_data,
):
    resources = get_test_data("migrations/0_11_0a0.json")
    await database.resources.insert_many(resources)

    # run migration
    await _migration_fn("0_11_0a0")(database)
    resources = await database.resources.find({}).to_list()

    # assert the data has been fixed by the migration
    assert len(resources) > 0
    for res in resources:
        assert "config" in res
        assert "common" not in res["config"]
        assert "general" in res["config"]
        assert "default_active" in res["config"]["general"]
        assert "sort_order" in res["config"]["general"]
        assert "default_collapsed" not in res["config"].get("special", {})
        assert "default_collapsed" in res["config"]["general"]

        for res_type_name in resource_types_mgr.list_names():
            assert res_type_name not in res["config"]

        # test "textAnnotation" type resource config structure
        if res["resource_type"] == "textAnnotation":
            assert "annotations" in res["config"]["special"]
            assert "groups" in res["config"]["special"]["annotations"]
            assert "display_template" in res["config"]["special"]["annotations"]
            assert "multi_value_delimiter" in res["config"]["special"]["annotations"]

        # test "locationMetadata" type resource config structure
        if res["resource_type"] == "locationMetadata":
            assert "item_display" in res["config"]["special"]
            assert "groups" in res["config"]["special"]["item_display"]
            assert "display_props" in res["config"]["special"]["item_display"]

        # test "apiCall" type resource config structure
        if res["resource_type"] == "apiCall":
            assert "api_call" in res["config"]["special"]
            assert "endpoint" in res["config"]["special"]["api_call"]
            assert "method" in res["config"]["special"]["api_call"]
            assert "content_type" in res["config"]["special"]["api_call"]
            assert "transform" in res["config"]["special"]
            assert "deps" in res["config"]["special"]["transform"]


@pytest.mark.anyio
async def test_0_11_1a0(
    database,
    get_test_data,
):
    resources = get_test_data("migrations/0_11_1a0.json")
    await database.resources.insert_many(resources)

    # run migration
    await _migration_fn("0_11_1a0")(database)
    resources = await database.resources.find({}).to_list()

    # assert the data has been fixed by the migration
    assert len(resources) > 0
    for res in resources:
        assert "config" in res
        assert "general" in res["config"]
        assert "default_collapsed" not in res["config"]["general"]
        if "collapsible_contents" in res["config"]["general"]:
            assert isinstance(res["config"]["general"]["collapsible_contents"], int)


@pytest.mark.anyio
async def test_0_12_0a0(
    database,
    get_test_data,
):
    collections = get_test_data("migrations/0_12_0a0.json")
    for coll in collections:
        await database[coll].insert_many(collections[coll])

    # run migration
    await _migration_fn("0_12_0a0")(database)

    # assert the data has been fixed by the migration

    # 1.: test "locationMetadata" resources
    resources = await database.resources.find(
        {"resource_type": "locationMetadata"}
    ).to_list()
    assert len(resources) > 0
    for res in resources:
        assert "config" in res
        assert "special" in res["config"]
        assert "item_display" not in res["config"]["special"]
        assert "entries_integration" in res["config"]["special"]
        ii_cfg = res["config"]["special"]["entries_integration"]
        assert "groups" in ii_cfg
        assert len(ii_cfg["groups"]) == 1
        assert ii_cfg["groups"][0]["key"] == "stanza_no"
        assert "item_props" in ii_cfg
        assert len(ii_cfg["item_props"]) == 2
        assert ii_cfg["item_props"][0]["key"] == "stanza_no_num"
        assert (
            ii_cfg["item_props"][0]["translations"][0]["translation"] == "# in numbers"
        )
        assert ii_cfg["item_props"][1]["key"] == "stanza_no_word"
        assert ii_cfg["item_props"][1]["translations"][0]["translation"] == "# in words"

    # 2.: test "textAnnotation" resources
    resources = await database.resources.find(
        {"resource_type": "textAnnotation"}
    ).to_list()
    assert len(resources) > 0
    for res in resources:
        assert "config" in res
        assert "special" in res["config"]
        assert "annotations" in res["config"]["special"]
        assert "groups" not in res["config"]["special"]["annotations"]
        assert "anno_integration" in res["config"]["special"]["annotations"]
        oag_cfg = res["config"]["special"]["annotations"]["anno_integration"]
        assert "groups" in oag_cfg
        assert len(oag_cfg["groups"]) == 1
        assert oag_cfg["groups"][0]["key"] == "entity"
        assert "item_props" in oag_cfg
        assert len(oag_cfg["item_props"]) == 2
        assert oag_cfg["item_props"][0]["key"] == "foo"
        assert oag_cfg["item_props"][0]["translations"][0]["translation"] == "foo"
        assert oag_cfg["item_props"][1]["key"] == "bar"
        assert oag_cfg["item_props"][1]["translations"][0]["translation"] == "bar"


@pytest.mark.anyio
async def test_0_13_0a0(
    database,
    get_test_data,
):
    contents = get_test_data("migrations/0_13_0a0.json")
    await database.contents.insert_many(contents)

    # run migration
    await _migration_fn("0_13_0a0")(database)
    contents = await database.contents.find({}).to_list()

    # assert the data has been fixed by the migration
    assert len(contents) == 3
    for content in contents:
        assert "comment" not in content
        assert "notes" not in content
        assert content.get("authors_comment") == "FOO"
        assert content.get("editors_comment") == "BAR"


@pytest.mark.anyio
async def test_0_17_0a0(
    database,
    get_test_data,
):
    data = get_test_data("migrations/0_17_0a0.json")
    await database.texts.insert_many(data["texts"])
    await database.resources.insert_many(data["resources"])

    # run migration
    await _migration_fn("0_17_0a0")(database)
    texts = await database.texts.find({}).to_list()
    resources = await database.resources.find({}).to_list()

    # assert the data has been fixed by the migration
    assert len(texts) > 0
    for text in texts:
        assert "pinned_metadata_ids" not in text
    assert len(resources) > 0
    for res in resources:
        assert "config" in res
        assert "special" in res["config"]
        assert "embed_as_tags" in res["config"]["special"]
        assert res["config"]["special"]["embed_as_tags"]


@pytest.mark.anyio
async def test_0_19_0a0(
    database,
    get_test_data,
):
    contents = get_test_data("migrations/0_19_0a0.json")
    await database.contents.insert_many(contents)

    # run migration
    await _migration_fn("0_19_0a0")(database)
    contents = await database.contents.find({}).to_list()

    # assert the data has been fixed by the migration
    eol_count = 0
    for content in contents:
        assert "tokens" in content
        for token in content["tokens"]:
            assert "token" not in token
            assert "lb" not in token
            assert (
                len(
                    [
                        anno["value"]
                        for anno in token["annotations"]
                        if anno["key"] == "form"
                    ]
                )
                == 1
            )

            assert "annotations" in token
            for anno in token["annotations"]:
                if anno["key"] == "eol":
                    eol_count += 1
    assert eol_count == 2


@pytest.mark.anyio
async def test_0_22_0a0(
    database,
    get_test_data,
):
    collections = get_test_data("migrations/0_22_0a0.json")
    for coll_name in collections:
        await database[coll_name].insert_many(collections[coll_name])

    # run migration
    await _migration_fn("0_22_0a0")(database)

    # assert resource data has been fixed by the migration
    for res in await database.resources.find({"resource_type": "apiCall"}).to_list():
        assert "config" in res
        assert "special" in res["config"]
        assert "api_call" not in res["config"]["special"]

    # assert contents data has been fixed by the migration
    for content in await database.contents.find({"resource_type": "apiCall"}).to_list():
        assert "query" not in content
        assert "transform_context" not in content
        assert "calls" in content
        assert len(content["calls"]) == 1
        call = content["calls"][0]
        assert "key" in call
        assert "endpoint" in call
        assert "method" in call
        assert "content_type" in call
        assert "query" in call
        assert "transform_context" in call
