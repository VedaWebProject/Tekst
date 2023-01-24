import abc

from beanie import PydanticObjectId

# from fastapi import HTTPException, status
from pydantic import Field

# from textrig.db.io import DbIO
# from textrig.logging import log
from textrig.models.common import AllOptional, DocumentBase, Metadata, ModelBase


class UnitBase(abc.ABC, ModelBase, DocumentBase):
    """A base class for types of data units belonging to a certain data layer"""

    layer_id: PydanticObjectId = Field(..., description="Data layer ID")
    node_id: PydanticObjectId = Field(..., description="Parent text node ID")
    meta: Metadata = Field(
        None,
        description="Arbitrary metadata on this layer unit",
        extra={"template": True},
    )

    class Settings:
        name = "units"
        is_root = True

    @classmethod
    @abc.abstractmethod
    def get_layer_type_plugin_class(cls) -> type:
        ...


class UnitUpdateBase(UnitBase, metaclass=AllOptional):
    pass
