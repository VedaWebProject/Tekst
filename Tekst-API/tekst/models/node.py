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
from tekst.models.text import TextDocument


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

    @classmethod
    async def get_node_locations(
        cls,
        text_id: PydanticObjectId,
        for_level: int | None = None,
        loc_delim: str | None = ", ",
    ) -> dict[str, str]:
        if for_level is not None and for_level < 0:
            for_level = 0
        if for_level is None or loc_delim is None:
            text = await TextDocument.get(text_id)
            for_level = len(text.levels) - 1 if for_level is None else for_level
            loc_delim = text.loc_delim if loc_delim is None else loc_delim
        node_labels = {}
        for level in range(for_level + 1):
            node_labels = {
                str(n.id): loc_delim.join(
                    [lbl for lbl in [node_labels.get(str(n.parent_id)), n.label] if lbl]
                )
                for n in await NodeDocument.find(
                    NodeDocument.text_id == text_id,
                    NodeDocument.level == level,
                )
                .sort(+NodeDocument.position)
                .to_list()
            }
        return node_labels


NodeCreate = Node.create_model()
NodeRead = Node.read_model()
NodeUpdate = Node.update_model()


class DeleteNodeResult(ModelBase):
    units: int
    nodes: int
