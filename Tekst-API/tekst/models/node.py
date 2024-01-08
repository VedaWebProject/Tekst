from typing import Annotated

from beanie import PydanticObjectId
from pydantic import (
    Field,
    StringConstraints,
)

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
)


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
        StringConstraints(min_length=1, max_length=256, strip_whitespace=True),
        Field(description="Label for identifying this text node in level context"),
    ]


class NodeDocument(Node, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "nodes"
        indexes = ["text_id", "parent_id", "level", "position"]


NodeCreate = Node.create_model()
NodeRead = Node.read_model()
NodeUpdate = Node.update_model()


class DeleteNodeResult(ModelBase):
    units: int
    nodes: int
