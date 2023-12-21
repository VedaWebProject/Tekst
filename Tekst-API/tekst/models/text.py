import re

from typing import Annotated

from beanie import PydanticObjectId
from pydantic import (
    Field,
    PlainSerializer,
    StringConstraints,
    field_validator,
)
from pydantic_extra_types.color import Color

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
    TranslationBase,
    Translations,
)


class TextSubtitleTranslation(TranslationBase):
    translation: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class TextLevelTranslation(TranslationBase):
    translation: Annotated[str, StringConstraints(min_length=1, max_length=32)]


AccentColor = Annotated[
    Color, PlainSerializer(lambda c: c.as_hex(), return_type=str, when_used="always")
]


class Text(ModelBase, ModelFactoryMixin):
    """A text represented in Tekst"""

    title: Annotated[
        str, Field(min_length=1, max_length=64, description="Title of this text")
    ]

    slug: Annotated[
        str,
        Field(
            pattern=r"^[a-z0-9]+$",
            min_length=1,
            max_length=16,
            description="A short identifier for use in URLs and internal operations",
        ),
    ]

    subtitle: Annotated[
        Translations[TextSubtitleTranslation],
        Field(
            description=(
                "Subtitle translations of this text "
                "(if set, it must contain at least one element)"
            ),
        ),
    ] = []

    levels: Annotated[
        list[Translations[TextLevelTranslation]],
        Field(
            description="Structure levels of this text and their label translations",
            min_length=1,
            max_length=32,
        ),
    ]

    default_level: Annotated[
        int,
        Field(
            ge=0,
            description=(
                "Default structure level for the client "
                "to use for browsing this text"
            ),
        ),
    ] = 0

    loc_delim: Annotated[
        str,
        Field(
            ", ",
            min_length=1,
            max_length=3,
            description="Delimiter for displaying text locations",
        ),
    ] = ", "

    labeled_location: Annotated[
        bool,
        Field(
            description=(
                "Whether the UI should label the parts of "
                "the browse location with each levels' names"
            ),
        ),
    ] = True

    accent_color: Annotated[
        AccentColor,
        Field(
            description="Accent color used for this text in the client UI",
        ),
    ] = "#305D97"

    is_active: Annotated[
        bool,
        Field(
            description=(
                "Whether the text should be listed "
                "for non-admin users in the web client"
            ),
        ),
    ] = False

    @field_validator("subtitle", mode="after")
    @classmethod
    def validate_subtitle(cls, v) -> Translations[TextSubtitleTranslation] | None:
        for subtitle in v:
            subtitle["translation"] = re.sub(
                r"[\s\n\r]+", " ", subtitle["translation"]
            ).strip()
        return v

    @field_validator("default_level", mode="after")
    @classmethod
    def validate_default_level(cls, v, info, **kwargs):
        if "levels" in info.data and v >= len(info.data["levels"]):
            raise ValueError(
                f"Invalid default level value ({v}). "
                f"This text only has {len(info.data['levels'])} levels."
            )
        return v


class TextDocument(Text, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "texts"
        bson_encoders = {Color: lambda c: c.as_hex()}

    @classmethod
    async def get_active_texts_ids(cls):
        return [
            text.id
            for text in await TextDocument.find(
                TextDocument.is_active == True  # noqa: E712
            ).to_list()
        ]


TextCreate = Text.create_model()
TextRead = Text.read_model()
TextUpdate = Text.update_model()


class InsertLevelRequest(ModelBase):
    translations: Annotated[
        Translations[TextLevelTranslation],
        Field(description="Translation(s) for the label of the level to insert"),
    ]


class MoveNodeRequestBody(ModelBase):
    position: int
    after: bool
    parent_id: Annotated[PydanticObjectId | None, Field(alias="parentId")]
