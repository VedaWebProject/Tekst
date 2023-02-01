from beanie import PydanticObjectId

# from fastapi import HTTPException, status
from pydantic import Field

# from textrig.db.io import DbIO
# from textrig.logging import log
from textrig.models.common import Metadata, ModelBase


class UnitBase(ModelBase):
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
    def get_layer_type_plugin_class(cls) -> type:
        raise NotImplementedError(
            "Method UnitBase.get_layer_type_plugin_class must be overridden!"
        )


# generate document model for this base model
# (used as a document root by child models)
UnitBase.get_document_model()
