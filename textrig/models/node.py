from pydantic import Field
from textrig.models.common import (
    AllOptional,
    Metadata,
    ObjectInDB,
    PyObjectId,
    TextRigBaseModel,
)


class Node(TextRigBaseModel):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_slug: str = Field(..., description="Slug of the text this node belongs to")
    parent_id: PyObjectId = Field(None, description="ID of parent node")
    level: int = Field(
        ..., description="Index of structure level this node is on", ge=0
    )
    index: int = Field(
        ..., description="Position among all text nodes on this level", ge=0
    )
    label: str = Field(..., description="Label for identifying this text node")
    meta: Metadata = Field(None, description="Arbitrary metadata")


class NodeRead(Node, ObjectInDB):

    ...


class NodeUpdate(Node, metaclass=AllOptional):

    ...
