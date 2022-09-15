import pytest
from pydantic.error_wrappers import ValidationError
from textrig.models.text import Level, Text


def test_validation():
    with pytest.raises(ValidationError) as error:
        Text()
        assert "missing" in error.value
    t = Text(title="agním īḷe puróhitaṁ", structure=[Level(label="Dummy Level")])
    assert t.safe_title == "agnim_ile_purohitam"


def test_composition(dummy_data_text):
    text = dummy_data_text
    assert text.title == "Rigveda"
    assert len(text.structure) == 3
    assert text.structure[1].label == "Hymn"


def test_min_levels():
    with pytest.raises(ValidationError):
        Text(title="Test-Text", structure=[])
