from typing import Annotated

from beanie import PydanticObjectId
from pydantic import (
    Field,
    PlainSerializer,
    StringConstraints,
    field_validator,
)
from pydantic_extra_types.color import Color
from typing_extensions import TypedDict

from tekst.models.common import (
    DocumentBase,
    Locale,
    ModelBase,
    ModelFactoryMixin,
)


class SubtitleTranslation(TypedDict):
    locale: Locale
    subtitle: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class StructureLevelTranslation(TypedDict):
    locale: Locale
    label: Annotated[str, StringConstraints(min_length=1, max_length=32)]


StructureLevelTranslations = Annotated[
    list[StructureLevelTranslation], Field(min_length=1)
]

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
        list[SubtitleTranslation] | None,
        Field(
            description=(
                "Subtitle translations of this text "
                "(if set, it must contain at least one element)"
            ),
            min_length=1,
            max_length=32,
        ),
    ] = None

    levels: Annotated[
        list[StructureLevelTranslations], Field(min_length=1, max_length=32)
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
        StringConstraints(min_length=1, max_length=3),
        Field(
            ", ",
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
    def validate_subtitle(cls, v) -> list[SubtitleTranslation] | None:
        if v is not None and len(v) < 1:
            return None
        return v

    @field_validator("default_level", mode="after")
    @classmethod
    def validate_default_level(cls, v, info, **kwargs):
        if info.data["levels"] and v >= len(info.data["levels"]):
            raise ValueError(
                f"Invalid default level value ({v}). "
                f"This text only has {len(info.data['levels'])} levels."
            )
        return v


class TextDocument(Text, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "texts"
        bson_encoders = {Color: lambda c: c.as_hex()}


TextCreate = Text.create_model()
TextRead = Text.read_model()
TextUpdate = Text.update_model()


class Node(ModelBase, ModelFactoryMixin):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_id: Annotated[
        PydanticObjectId, Field(description="ID of the text this node belongs to")
    ]
    parent_id: Annotated[
        PydanticObjectId | None, Field(description="ID of parent node")
    ] = None
    level: Annotated[
        int, Field(ge=0, lt=32, description="Index of structure level this node is on")
    ]
    position: Annotated[
        int, Field(ge=0, description="Position among all text nodes on this level")
    ]
    label: Annotated[
        str,
        StringConstraints(min_length=1, max_length=256),
        Field(description="Label for identifying this text node in level context"),
    ]


class NodeDocument(Node, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "nodes"
        indexes = ["text_id", "parent_id", "level", "position"]


NodeCreate = Node.create_model()
NodeRead = Node.read_model()
NodeUpdate = Node.update_model()


class InsertLevelRequest(ModelBase):
    translations: Annotated[
        list[StructureLevelTranslation], Field(min_length=1)
    ] = Field(..., description="Translation(s) for the label of the level to insert")


class DeleteNodeResult(ModelBase):
    units: int
    nodes: int


class MoveNodeRequestBody(ModelBase):
    position: int
    after: bool
    parent_id: Annotated[PydanticObjectId | None, Field(alias="parentId")]
