from abc import ABC

from pydantic import Field
from textrig.models.common import (
    AllOptional,
    DbDocument,
    DocumentId,
    Metadata,
    TextRigBaseModel,
)


class UnitBase(ABC, TextRigBaseModel):
    """A base class for types of data units belonging to a certain data layer"""

    layer_id: DocumentId = Field(..., description="Data layer ID")
    node_id: DocumentId = Field(..., description="Parent text node ID")
    meta: Metadata = Field(
        None,
        description="Arbitrary metadata on this layer unit",
        extra={"template": True},
    )


class UnitReadBase(UnitBase, DbDocument):
    ...


class UnitUpdateBase(UnitBase, DbDocument, metaclass=AllOptional):
    ...
