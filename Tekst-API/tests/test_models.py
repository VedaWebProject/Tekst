import pytest

from pydantic import ValidationError
from tekst.models.content import ContentBase
from tekst.models.resource import ResourceBase
from tekst.models.resource_configs import ItemIntegrationConfig
from tekst.models.text import Text, TextCreate, TextDocument, TextRead, TextUpdate
from tekst.models.user import UserReadPublic


def test_basic_validation():
    with pytest.raises(ValidationError) as error:
        TextRead()
        assert "missing" in error.value


def test_serialization(get_test_data):
    test_data = get_test_data("collections/texts.json")
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


def test_resource_subtitle_validator():
    # desc with arbitrary whitespaces
    from tekst.resources.plain_text import PlainTextResource

    resource = PlainTextResource(
        title=[
            {
                "locale": "*",
                "translation": "foo",
            }
        ],
        text_id="5eb7cfb05e32e07750a1756a",
        level=0,
        resource_type="plainText",
        subtitle=[
            {
                "locale": "enUS",
                "translation": "foo      bar\t\t   baz\n \ttest",
            }
        ],
    )
    assert resource.subtitle[0]["translation"] == "foo bar baz test"
    # desc = None
    resource = PlainTextResource(
        title=[{"locale": "*", "translation": "foo"}],
        text_id="5eb7cfb05e32e07750a1756a",
        level=0,
        resource_type="plainText",
    )
    assert isinstance(resource.subtitle, list)
    assert len(resource.subtitle) == 0


def test_user_read_public():
    urp = UserReadPublic(
        id="5eb7cfb05e32e07750a1756a",
        username="fooBar",
        name="Foo Bar",
        affiliation="Baz",
        is_superuser=False,
        is_active=True,
        avatar_url=None,
        bio=None,
        public_fields=["name"],
    )
    assert not urp.affiliation


@pytest.mark.anyio
async def test_text_get_full_loc_labels_invalid_level(insert_test_data):
    text_id = (await insert_test_data())["texts"][0]
    text_doc: TextDocument = await TextDocument.get(text_id)
    with pytest.raises(ValueError):
        await text_doc.full_location_labels(42)


def test_text_valid_default_level():
    with pytest.raises(ValidationError):
        TextCreate(
            title="foo",
            slug="foo",
            levels=[[{"locale": "enUS", "translation": "foo"}]],
            default_level=2,
        )


def test_text_valid_default_color():
    t = Text(
        title="foo",
        slug="foo",
        levels=[[{"locale": "enUS", "translation": "foo"}]],
    )
    t.model_dump()


def test_resource_type_validator(wrong_id):
    with pytest.raises(ValidationError):
        ResourceBase(
            resource_type="foo_bar",
            title="Foo Bar",
        )
    with pytest.raises(ValidationError):
        ContentBase(
            resource_id=wrong_id,
            resource_type="foo_bar",
            location_id=wrong_id,
        )


@pytest.mark.anyio
async def test_apply_updates(test_app):
    text = TextCreate(
        title="Foo",
        subtitle=[{"locale": "enUS", "translation": "foo"}],
        slug="foo",
        levels=[[{"locale": "enUS", "translation": "foo"}]],
        loc_delim=" > ",
        accent_color="#FF0000",
    )
    assert text.labeled_location
    text_doc = TextDocument.model_from(text)
    await text_doc.create()
    assert text_doc.accent_color.as_rgb() == "rgb(255, 0, 0)"
    assert text_doc.id
    text_updates = TextUpdate(slug="bar", loc_delim=None)
    text_doc = await text_doc.apply_updates(text_updates)
    assert text_doc.slug == "bar"
    assert text_doc.loc_delim == " > "  # apply_updates should ignore None
    text_read = TextRead.model_from(text_doc)
    assert text_read.slug == "bar"
    assert text_read.id


def test_item_integration_config():
    ii_cfg = ItemIntegrationConfig(
        groups=[
            {"key": "foo", "translations": [{"locale": "*", "translation": "Foo"}]},
            {"key": "bar", "translations": [{"locale": "*", "translation": "Bar"}]},
        ],
        item_props=[
            {
                "key": "one",
                "translations": [{"locale": "*", "translation": "One"}],
                "group": "bar",
            },
            {
                "key": "two",
                "translations": [{"locale": "*", "translation": "Two"}],
                "group": "bar",
            },
            {
                "key": "three",
                "translations": [{"locale": "*", "translation": "Three"}],
                "group": "foo",
            },
            {
                "key": "four",
                "translations": [{"locale": "*", "translation": "Four"}],
                "group": "foo",
            },
        ],
    )

    sorted_keys = ii_cfg.sorted_item_keys(["three", "four", "one"])
    assert str(sorted_keys) == str(["three", "four", "one"])
    assert str(ii_cfg.sorted_item_keys()) == str(["three", "four", "one", "two"])
