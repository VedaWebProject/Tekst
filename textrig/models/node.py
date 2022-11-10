from pydantic import Field
from textrig.models.common import (
    AllOptional,
    DbObject,
    DocId,
    Metadata,
    TextRigBaseModel,
)


class Node(TextRigBaseModel):
    """A node in a text structure (e.g. chapter, paragraph, ...)"""

    text_slug: str = Field(..., description="Slug of the text this node belongs to")
    parent_id: DocId = Field(None, description="ID of parent node")
    level: int = Field(
        ..., description="Index of structure level this node is on", ge=0
    )
    index: int = Field(
        ..., description="Position among all text nodes on this level", ge=0
    )
    label: str = Field(..., description="Label for identifying this text node")
    meta: Metadata = Field(None, description="Arbitrary metadata")


class NodeRead(Node, DbObject):
    """An existing node read from the database"""

    ...


class NodeUpdate(Node, metaclass=AllOptional):
    """An update to an existing node"""

    ...
