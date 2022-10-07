import pytest
from pydantic.error_wrappers import ValidationError
from textrig.models.text import Text, TextInDB


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


def test_composition(dummy_data_text):
    text = dummy_data_text
    assert text.title == "Rigveda"
    assert len(text.levels) == 3


def test_serialization(dummy_data_text):
    text = dummy_data_text
    dummy_id = "6331b6e05c474b9f8f19330f"
    assert text.dict().get("title")
    text = TextInDB(_id=dummy_id, **text.dict())
    assert str(text.dict().get("id", None)) == dummy_id
    assert str(text.dict(for_mongo=True).get("_id", None)) == dummy_id


def test_deserialization():
    data = {"title": "Foo", "locDelim": "+"}
    t = Text(**data)
    assert t.loc_delim == "+"
