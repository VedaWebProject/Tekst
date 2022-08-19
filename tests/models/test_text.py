import pytest
from pydantic.error_wrappers import ValidationError
from textrig.models.common import PyObjectId
from textrig.models.text import Text, TextLevel


def test_validation():
    with pytest.raises(ValidationError) as error:
        Text()
        assert "missing" in error.value
    t = Text(title="agním īḷe puróhitaṁ", levels=[TextLevel(label="Dummy Level")])
    assert t.label == "agnim_ile_purohitam"


def test_composition(dummy_data_text):
    text = dummy_data_text
    assert type(text.id) == PyObjectId
    assert text.title == "Rigveda"
    assert len(text.levels) == 3
    assert text.levels[1].label == "Hymn"


def test_mutability(dummy_data_text):
    text = dummy_data_text
    with pytest.raises(TypeError):
        text.levels = [TextLevel(label="Book")]


def test_min_levels():
    with pytest.raises(ValidationError):
        Text(title="Test-Text", levels=[])
