# from fastapi import HTTPException, status
# from textrig.utils.strings import safe_name
from pydantic import Field

# from textrig.db.io import DbIO
# from textrig.logging import log
from textrig.models.common import Metadata, ModelBase, PyObjectId


class Text(ModelBase):
    """A text represented in TextRig"""

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

    loc_delim: str = Field(
        ",",
        description="Delimiter for displaying text locations",
    )

    class Settings:
        name = "texts"


TextDocument = Text.get_document_model()
TextCreate = Text.get_create_model()
TextRead = Text.get_read_model()
TextUpdate = Text.get_update_model()


class Node(ModelBase):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_id: PyObjectId = Field(..., description="ID of the text this node belongs to")
    parent_id: PyObjectId = Field(None, description="ID of parent node")
    level: int = Field(
        ..., description="Index of structure level this node is on", ge=0
    )
    position: int = Field(
        ..., description="Position among all text nodes on this level", ge=0
    )
    label: str = Field(..., description="Label for identifying this text node")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    class Settings:
        name = "nodes"


NodeDocument = Node.get_document_model()
NodeCreate = Node.get_create_model()
NodeRead = Node.get_read_model()
NodeUpdate = Node.get_update_model()
