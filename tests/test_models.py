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


def test_dict_override(test_app):
    t_data = Text(title="agním īḷe puróhitaṁ", slug="agnim", levels=["foo"]).dict()
    assert t_data["title"] == "agním īḷe puróhitaṁ"
    assert "slug" in t_data
    assert t_data["slug"] == "agnim"
    assert "locDelim" not in t_data  # because exclude_unset in dict() override


def test_serialization(test_app, test_data):
    text = Text(**test_data["texts"][0])
    assert text.dict().get("title")
    dummy_id = "6331b6e05c474b9f8f19330f"
    text = Text(id=dummy_id, loc_delim="---", **test_data["texts"][0])
    assert "_id" in text.dict(by_alias=True)
    assert "locDelim" in text.dict(by_alias=True)
    assert "id" in text.dict()
    assert "loc_delim" in text.dict()


def test_deserialization(test_app):
    data = {"title": "Foo", "slug": "foo", "locDelim": "+", "levels": ["foo"]}
    t = Text(**data)
    assert t.loc_delim == "+"
    data = {"title": "Foo", "slug": "foo", "loc_delim": "+", "levels": ["foo"]}
    t = Text(**data)
    assert t.loc_delim == "+"


def test_model_field_casing(test_app):
    t = Text(title="foo", slug="foo", loc_delim="bar", levels=["foo"])
    assert t.title == "foo"
    assert t.loc_delim == "bar"


def test_layer_description_validator(test_app):
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
