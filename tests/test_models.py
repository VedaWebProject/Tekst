import pytest
from pydantic.error_wrappers import ValidationError
from textrig.models.text import Text, TextRead


def test_basic_validation():
    with pytest.raises(ValidationError) as error:
        Text()
        assert "missing" in error.value


def test_slug_generation():
    t = Text(title="agním īḷe puróhitaṁ")
    assert t.slug == "agnimilepurohita"


def test_dict_override():
    t_data = Text(title="agním īḷe puróhitaṁ").dict()
    assert t_data["title"] == "agním īḷe puróhitaṁ"
    assert "slug" in t_data
    assert t_data["slug"] == "agnimilepurohita"
    assert "loc_delim" not in t_data


def test_serialization(test_data):
    text = Text(**test_data["texts"][0])
    assert text.dict().get("title")
    dummy_id = "6331b6e05c474b9f8f19330f"
    text = TextRead(_id=dummy_id, **test_data["texts"][0])
    assert text.dict().get("id", False)
    assert text.dict(for_mongo=True).get("_id", False)


def test_deserialization():
    data = {"title": "Foo", "locDelim": "+"}
    t = Text(**data)
    assert t.loc_delim == "+"


def test_model_field_casing():
    t = Text(title="foo", loc_delim="bar")
    assert t.title == "foo"
    assert t.loc_delim == "bar"
    t = Text(title="foo", locDelim="bar")
    assert t.loc_delim == "bar"
