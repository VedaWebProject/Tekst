import pytest
from pydantic.error_wrappers import ValidationError
from textrig.models.text import Text


def test_validation():
    with pytest.raises(ValidationError) as error:
        Text()
        assert "missing" in error.value
    t = Text(title="agním īḷe puróhitaṁ")
    assert t.slug == "agnim_ile_purohitam"


def test_composition(dummy_data_text):
    text = dummy_data_text
    assert text.title == "Rigveda"
    assert len(text.levels) == 3
