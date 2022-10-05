import pytest
from pydantic.error_wrappers import ValidationError
from textrig.models.text import Text


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
