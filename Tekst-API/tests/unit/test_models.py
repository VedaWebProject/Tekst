from datetime import datetime

import pytest

from pydantic.error_wrappers import ValidationError
from tekst.models.text import TextCreate, TextRead


def test_basic_validation():
    with pytest.raises(ValidationError) as error:
        TextRead()
        assert "missing" in error.value


def test_dict_override(test_app):
    t_data = TextCreate(
        title="agním īḷe puróhitaṁ",
        slug="agnim",
        levels=[[{"locale": "enUS", "label": "foo"}]],
    ).model_dump()
    assert t_data["title"] == "agním īḷe puróhitaṁ"
    assert "slug" in t_data
    assert t_data["slug"] == "agnim"
    assert "locDelim" not in t_data  # because exclude_unset in model_dump() override


def test_serialization(test_app, test_data):
    text = TextCreate(**test_data["texts"][0])
    assert text.model_dump().get("title")
    dummy_id = "6331b6e05c474b9f8f19330f"
    text = TextRead(
        id=dummy_id,
        loc_delim="---",
        **test_data["texts"][0],
    )
    assert "id" in text.model_dump()
    assert "locDelim" in text.model_dump()
    assert "loc_delim" in text.model_dump(by_alias=False)
    text = TextRead(
        **{
            "id": dummy_id,
            "createdAt": datetime.now(),
            "modifiedAt": datetime.now(),
            **test_data["texts"][0],
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
    from tekst.layer_types.plaintext import PlainTextLayer

    layer = PlainTextLayer(
        title="foo",
        text="5eb7cfb05e32e07750a1756a",
        level=0,
        layer_type="plaintext",
        description="foo      bar\t\t   baz\n \ttest",
    )
    assert layer.description == "foo bar baz test"
    # desc = None
    layer = PlainTextLayer(
        title="foo",
        text="5eb7cfb05e32e07750a1756a",
        level=0,
        layer_type="plaintext",
        description=None,
    )
    assert layer.description is None
