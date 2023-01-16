import pytest
from pydantic.error_wrappers import ValidationError
from textrig.models.text import Text


def test_basic_validation():
    with pytest.raises(ValidationError) as error:
        Text()
        assert "missing" in error.value


# def test_slug_generation():
#     t = Text(title="agním īḷe puróhitaṁ", slug="agnim", levels=["foo"])
#     assert t.slug == "agnimilepurohita"


def test_dict_override():
    t_data = Text(title="agním īḷe puróhitaṁ", slug="agnim", levels=["foo"]).dict()
    assert t_data["title"] == "agním īḷe puróhitaṁ"
    assert "slug" in t_data
    assert t_data["slug"] == "agnim"
    assert "loc_delim" not in t_data


def test_serialization(test_data):
    text = Text(**test_data["texts"][0])
    assert text.dict().get("title")
    dummy_id = "6331b6e05c474b9f8f19330f"
    text = Text(id=dummy_id, **test_data["texts"][0])
    assert text.dict().get("id", False)


def test_deserialization():
    data = {"title": "Foo", "slug": "foo", "loc_delim": "+", "levels": ["foo"]}
    t = Text(**data)
    assert t.loc_delim == "+"


def test_model_field_casing():
    t = Text(title="foo", slug="foo", loc_delim="bar", levels=["foo"])
    assert t.title == "foo"
    assert t.loc_delim == "bar"


def test_layer_description_validator():
    # desc with arbitrary whitespaces
    from textrig.layer_types.plaintext import PlainTextLayer

    layer = PlainTextLayer(
        title="foo",
        text_slug="foo",
        level=0,
        layer_type="plaintext",
        description="foo      bar\t\t   baz\n \ttest",
    )
    assert layer.description == "foo bar baz test"
    # desc = None
    layer = PlainTextLayer(
        title="foo",
        text_slug="foo",
        level=0,
        layer_type="plaintext",
        description=None,
    )
    assert layer.description is None
