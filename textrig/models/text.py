from pydantic import Field, root_validator
from textrig.models.common import (
    AllOptional,
    DbDocument,
    DocumentId,
    Metadata,
    TextRigBaseModel,
)
from textrig.utils.strings import safe_name


class Text(TextRigBaseModel):
    """A text represented in TextRig"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this text"
    )

    slug: str = Field(
        None,
        regex=r"^[a-z][a-z0-9\-_]{0,14}[a-z0-9]$",
        min_length=2,
        max_length=16,
        description=(
            "A short identifier string for use in URLs and internal operations "
            "(will be generated automatically if missing)"
        ),
    )

    subtitle: str = Field(
        None, min_length=1, max_length=128, description="Subtitle of this text"
    )

    levels: list[str] = Field(list(), min_items=1)

    loc_delim: str = Field(
        ",",
        description="Delimiter for displaying text locations",
    )

    @root_validator(pre=True)
    def generate_dynamic_defaults(cls, values) -> dict:
        # generate slug if none is given
        if "slug" not in values:
            if not values.get("title", None):
                values["slug"] = "text"
            else:
                values["slug"] = safe_name(
                    values.get("title"), min_len=2, max_len=16, delim=""
                )
        return values


class TextRead(Text, DbDocument):
    """An existing text read from the database"""

    ...


class TextUpdate(Text, DbDocument, metaclass=AllOptional):
    """An update to an existing text"""

    ...


class Node(TextRigBaseModel):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_slug: str = Field(..., description="Slug of the text this node belongs to")
    parent_id: DocumentId = Field(None, description="ID of parent node")
    level: int = Field(
        ..., description="Index of structure level this node is on", ge=0
    )
    index: int = Field(
        ..., description="Position among all text nodes on this level", ge=0
    )
    label: str = Field(..., description="Label for identifying this text node")
    meta: Metadata = Field(None, description="Arbitrary metadata")


class NodeRead(Node, DbDocument):
    """An existing node read from the database"""

    ...


class NodeUpdate(Node, DbDocument, metaclass=AllOptional):
    """An update to an existing node"""

    ...
