from typing import List

from pydantic import Field, StringConstraints, field_validator
from pydantic_extra_types.color import Color
from typing_extensions import Annotated, TypedDict

from tekst.models.common import (
    DocumentBase,
    Locale,
    Metadata,
    ModelBase,
    ModelFactory,
    PyObjectId,
)


class SubtitleTranslation(TypedDict):
    locale: Locale
    subtitle: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class StructureLevelTranslation(TypedDict):
    locale: Locale
    label: Annotated[str, StringConstraints(min_length=1, max_length=32)]


class Text(ModelBase, ModelFactory):
    """A text represented in Tekst"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this text"
    )

    slug: str = Field(
        ...,
        pattern=r"^[a-z0-9]+$",
        min_length=1,
        max_length=16,
        description=("A short identifier for use in URLs and internal operations"),
    )

    subtitle: list[SubtitleTranslation] | None = Field(
        None,
        description=(
            "Subtitle translations of this text "
            "(if set, it must contain at least one element)"
        ),
    )

    levels: list[
        Annotated[List[StructureLevelTranslation], Field(min_length=1)]
    ] = Field(..., min_length=1, max_length=32)

    default_level: Annotated[int, Field(ge=0)] = Field(
        0,
        description=(
            "Default structure level for the client to use for browsing this text"
        ),
    )

    loc_delim: Annotated[str, StringConstraints(min_length=1, max_length=3)] = Field(
        ", ",
        description="Delimiter for displaying text locations",
    )

    labeled_location: bool = Field(
        True,
        description=(
            "Whether the UI should label the parts of "
            "the browse location with each levels' names"
        ),
    )

    accent_color: Color = Field(
        default_factory=lambda: Color("#305D97"),
        description="Accent color used for this text in the client UI",
    )

    is_active: bool = Field(
        False,
        description=(
            "Whether the text should be listed " "for non-admin users in the web client"
        ),
    )

    @field_validator("subtitle")
    @classmethod
    def validate_subtitle(cls, v) -> list[SubtitleTranslation] | None:
        if v is not None and len(v) < 1:
            return None
        return v

    @field_validator("default_level")
    @classmethod
    def validate_default_level(cls, v, info, **kwargs):
        if info.data["levels"] and v >= len(info.data["levels"]):
            raise ValueError(
                f"Invalid default level value ({v}). "
                f"This text only has {len(info.data['levels'])} levels."
            )
        return v

    @field_validator("accent_color")
    @classmethod
    def validate_color(cls, v) -> Color:
        if not isinstance(v, Color):
            try:
                v = Color(v)
            except Exception:
                return None
        return v.as_hex()

    class Settings:
        name = "texts"


# TextDocument = Text.get_document_model()
class TextDocument(Text, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "texts"
        bson_encoders = {Color: lambda c: str(c)}


TextCreate = Text.get_create_model()
TextRead = Text.get_read_model()
TextUpdate = Text.get_update_model()


class Node(ModelBase, ModelFactory):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_id: PyObjectId = Field(..., description="ID of the text this node belongs to")
    parent_id: PyObjectId = Field(None, description="ID of parent node")
    level: Annotated[int, Field(ge=0, lt=32)] = Field(
        ..., description="Index of structure level this node is on"
    )
    position: Annotated[int, Field(ge=0)] = Field(
        ..., description="Position among all text nodes on this level"
    )
    label: Annotated[str, StringConstraints(min_length=1, max_length=256)] = Field(
        ..., description="Label for identifying this text node in level context"
    )
    meta: Metadata | None = Field(None, description="Arbitrary metadata")


class NodeDocument(Node, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "nodes"
        indexes = ["textId", "parentId", "level", "position"]


NodeCreate = Node.get_create_model()
NodeRead = Node.get_read_model()
NodeUpdate = Node.get_update_model()


class InsertLevelRequest(ModelBase):
    translations: Annotated[
        List[StructureLevelTranslation], Field(min_length=1)
    ] = Field(..., description="Translation(s) for the label of the level to insert")
