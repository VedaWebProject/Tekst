from pydantic import Field, conint, validator
from pydantic.color import Color

from tekst.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    ModelFactory,
    PyObjectId,
)


class Text(ModelBase, ModelFactory):
    """A text represented in Tekst"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this text"
    )

    slug: str = Field(
        ...,
        regex=r"^[a-z][a-z0-9\-_]{0,14}[a-z0-9]$",
        min_length=2,
        max_length=16,
        description=(
            "A short identifier string for use in URLs and internal operations"
        ),
    )

    subtitle: str = Field(
        None, min_length=1, max_length=128, description="Subtitle of this text"
    )

    levels: list[str] = Field(..., min_items=1)

    default_level: conint(ge=0) = Field(
        0,
        description=(
            "Default structure level for the client to use for browsing this text"
        ),
    )

    loc_delim: str = Field(
        ",",
        description="Delimiter for displaying text locations",
    )

    labeled_levels: bool = Field(
        True,
        description=(
            "Whether the UI should label the nodes of "
            "the browse location with each levels' names"
        ),
    )

    accent_color: Color = Field(
        default_factory=lambda: Color("#18A058"),
        description="Accent color used for this text in the client UI",
    )

    @validator("default_level")
    def validate_default_level(cls, v, values, **kwargs):
        if v >= len(values["levels"]):
            raise ValueError(
                f"Invalid default level value ({v}). "
                f"This text only has {len(values['levels'])} levels."
            )
        return v

    @validator("accent_color")
    def validate_color(cls, v) -> Color:
        if not isinstance(v, Color):
            try:
                v = Color(v)
            except Exception:
                return None
        return v.as_hex()

    class Settings:
        name = "texts"


TextDocument = Text.get_document_model()
TextCreate = Text.get_create_model()
TextRead = Text.get_read_model()
TextUpdate = Text.get_update_model()


class Node(ModelBase, ModelFactory):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_id: PyObjectId = Field(..., description="ID of the text this node belongs to")
    parent_id: PyObjectId = Field(None, description="ID of parent node")
    level: int = Field(
        ..., description="Index of structure level this node is on", ge=0
    )
    position: int = Field(
        ..., description="Position among all text nodes on this level", ge=0
    )
    label: str = Field(
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
