import abc

from fastapi import HTTPException, status
from pydantic import Field
from textrig.db.io import DbIO
from textrig.logging import log
from textrig.models.common import (
    AllOptional,
    DbDocument,
    DocumentId,
    Metadata,
    TextRigBaseModel,
)


class UnitBase(abc.ABC, TextRigBaseModel):
    """A base class for types of data units belonging to a certain data layer"""

    layer_id: DocumentId = Field(..., description="Data layer ID")
    node_id: DocumentId = Field(..., description="Parent text node ID")
    meta: Metadata = Field(
        None,
        description="Arbitrary metadata on this layer unit",
        extra={"template": True},
    )

    @classmethod
    @abc.abstractmethod
    def get_layer_type_plugin_class(cls) -> type:
        ...

    @classmethod
    def collection_name(cls) -> str:
        return cls.get_layer_type_plugin_class().units_collection_name()

    async def create(self, db_io: DbIO) -> "UnitReadBase":
        unit_model = self.get_layer_type_plugin_class().get_unit_model()
        unit = self.ensure_model_type(unit_model)
        target_collection = self.collection_name()
        # check for conflicts
        if await db_io.find_one_by_example(
            target_collection, {"layer_id": unit.layer_id, "node_id": unit.node_id}
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Equal unit already exists",
            )
        # TODO: check if layer ID and node ID are valid!
        pass
        # insert new unit
        unit_data = await db_io.insert_one(target_collection, unit)
        log.debug(f"Created unit: {unit_data}")
        unit_read_model = self.get_layer_type_plugin_class().get_unit_read_model()
        return unit_read_model(**unit_data)


class UnitReadBase(UnitBase, DbDocument):
    @classmethod
    async def read(cls, doc_id: str | DocumentId, db_io: DbIO) -> "UnitReadBase":
        unit_data = await db_io.find_one(cls.collection_name(), doc_id)
        if not unit_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unit with ID {str(doc_id)} cannot be found",
            )
        unit_read_model = cls.get_layer_type_plugin_class().get_unit_read_model()
        return unit_read_model(**unit_data)


class UnitUpdateBase(UnitBase, DbDocument, metaclass=AllOptional):
    async def update(self, db_io: DbIO) -> UnitReadBase:
        target_collection = self.collection_name()
        updated_id = await db_io.update(target_collection, self)
        if not updated_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not update unit {self.id}",
            )
        unit_read_model = self.get_layer_type_plugin_class().get_unit_read_model()
        updated_unit = unit_read_model(
            **await db_io.find_one(target_collection, updated_id)
        )
        log.debug(f"Updated unit {updated_id}: {updated_unit.dict()}")
        return updated_unit
