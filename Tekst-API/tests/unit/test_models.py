import pytest

from pydantic.error_wrappers import ValidationError
from tekst.models.text import TextCreate, TextRead


def test_basic_validation():
    with pytest.raises(ValidationError) as error:
        TextRead()
        assert "missing" in error.value


def test_serialization(test_app, get_sample_data):
    test_data = get_sample_data("db/texts.json")
    text = TextCreate(**test_data[0])
    text.loc_delim = None
    assert text.model_dump().get("title")
    dummy_id = "6331b6e05c474b9f8f19330f"
    text = TextRead(
        id=dummy_id,
        loc_delim="---",
        **text.model_dump(exclude_none=True),
    )
    assert "id" in text.model_dump()
    assert "loc_delim" in text.model_dump()
    text = TextRead(
        **{
            "id": dummy_id,
            **test_data[0],
        }
    )
    assert str(text.id) == dummy_id


def test_deserialization(test_app):
    data = {
        "title": "Foo",
        "slug": "foo",
        "locDelim": "+",
        "levels": [[{"locale": "enUS", "label": "foo"}]],
    }
    t = TextCreate(**data)
    assert t.loc_delim == "+"
    data = {
        "title": "Foo",
        "slug": "foo",
        "loc_delim": "+",
        "levels": [[{"locale": "enUS", "label": "foo"}]],
    }
    t = TextCreate(**data)
    assert t.loc_delim == "+"


def test_model_field_casing(test_app):
    t = TextCreate(
        title="foo",
        slug="foo",
        loc_delim="bar",
        levels=[[{"locale": "enUS", "label": "foo"}]],
    )
    assert t.title == "foo"
    assert t.loc_delim == "bar"


def test_layer_description_validator(test_app):
    # desc with arbitrary whitespaces
    from tekst.layer_types.plaintext import PlaintextLayer

    layer = PlaintextLayer(
        title="foo",
        text="5eb7cfb05e32e07750a1756a",
        level=0,
        layer_type="plaintext",
        description="foo      bar\t\t   baz\n \ttest",
    )
    assert layer.description == "foo bar baz test"
    # desc = None
    layer = PlaintextLayer(
        title="foo",
        text="5eb7cfb05e32e07750a1756a",
        level=0,
        layer_type="plaintext",
        description=None,
    )
    assert layer.description is None
