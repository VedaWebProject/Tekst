import pytest

from pydantic.error_wrappers import ValidationError
from tekst.models.text import TextCreate, TextRead
from tekst.models.user import UserReadPublic


def test_basic_validation():
    with pytest.raises(ValidationError) as error:
        TextRead()
        assert "missing" in error.value


def test_serialization(get_sample_data):
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


def test_deserialization():
    data = {
        "title": "Foo",
        "slug": "foo",
        "locDelim": "+",
        "levels": [[{"locale": "enUS", "translation": "foo"}]],
    }
    t = TextCreate(**data)
    assert t.loc_delim == "+"
    data = {
        "title": "Foo",
        "slug": "foo",
        "loc_delim": "+",
        "levels": [[{"locale": "enUS", "translation": "foo"}]],
    }
    t = TextCreate(**data)
    assert t.loc_delim == "+"


def test_model_field_casing():
    t = TextCreate(
        title="foo",
        slug="foo",
        loc_delim="bar",
        levels=[[{"locale": "enUS", "translation": "foo"}]],
    )
    assert t.title == "foo"
    assert t.loc_delim == "bar"


def test_resource_description_validator():
    # desc with arbitrary whitespaces
    from tekst.resource_types.plaintext import PlaintextResource

    resource = PlaintextResource(
        title="foo",
        text_id="5eb7cfb05e32e07750a1756a",
        level=0,
        resource_type="plaintext",
        description=[
            {"locale": "enUS", "translation": "foo      bar\t\t   baz\n \ttest"}
        ],
    )
    assert resource.description[0]["translation"] == "foo bar baz test"
    # desc = None
    resource = PlaintextResource(
        title="foo",
        text_id="5eb7cfb05e32e07750a1756a",
        level=0,
        resource_type="plaintext",
    )
    assert isinstance(resource.description, list)
    assert len(resource.description) == 0


def test_user_read_public():
    urp = UserReadPublic(
        id="5eb7cfb05e32e07750a1756a",
        username="fooBar",
        name="Foo Bar",
        affiliation="Baz",
        public_fields=["name"],
    )
    assert not urp.affiliation
