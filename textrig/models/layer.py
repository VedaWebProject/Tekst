import abc
import re

from fastapi import HTTPException, status
from pydantic import Field, validator
from textrig.db.io import DbIO
from textrig.logging import log
from textrig.models.common import (
    AllOptional,
    DbDocument,
    DocumentId,
    Metadata,
    TextRigBaseModel,
)


class LayerBase(abc.ABC, TextRigBaseModel):
    """A data layer describing a set of data on a text"""

    title: str = Field(
        ..., min_length=1, max_length=64, description="Title of this layer"
    )
    description: str = Field(
        None,
        min_length=1,
        max_length=128,
        description="Short, one-line description of this data layer",
    )
    text_slug: str = Field(..., description="Slug of the text this layer belongs to")
    level: int = Field(..., description="Text level this layer belongs to")
    layer_type: str = Field(
        ..., description="A string identifying one of the available layer types"
    )
    # owner_id: DocId = Field(None)  # TODO: users don't exist, yet
    public: bool = Field(False, description="Publication status of this layer")
    meta: Metadata = Field(None, description="Arbitrary metadata")

    @validator("description")
    def handle_whitespaces_in_description(cls, v):
        if not isinstance(v, str):
            return None
        return re.sub(r"[\s\n]+", " ", v)

    @validator("layer_type")
    def validate_layer_type_name(cls, v):
        from textrig.layer_types import get_layer_type_names

        layer_type_names = get_layer_type_names()
        if v.lower() not in layer_type_names:
            raise ValueError(
                f"Given layer type ({v}) is not a valid "
                f"layer type name (one of {layer_type_names})."
            )
        return v.lower()

    @classmethod
    @abc.abstractmethod
    def get_layer_type_plugin_class(cls) -> type:
        ...

    async def create(self, db_io) -> "LayerReadBase":
        layer_model = self.get_layer_type_plugin_class().get_layer_model()
        layer = self.ensure_model_type(layer_model)
        if not await db_io.find_one("texts", layer.text_slug, "slug"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Corresponding text doesn't exist"
            )
        layer_data = await db_io.insert_one("layers", layer)
        log.debug(f"Created layer: {layer_data}")
        layer_read_model = self.get_layer_type_plugin_class().get_layer_read_model()
        return layer_read_model(**layer_data)


class LayerReadBase(LayerBase, DbDocument):
    """An existing data layer read from the database"""

    @classmethod
    async def read(cls, doc_id: str | DocumentId, db_io: DbIO) -> "LayerReadBase":
        layer_data = await db_io.find_one("layers", doc_id)
        if not layer_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Layer with ID {str(doc_id)} cannot be found",
            )
        layer_read_model = cls.get_layer_type_plugin_class().get_layer_read_model()
        return layer_read_model(**layer_data)


class LayerUpdateBase(LayerBase, DbDocument, metaclass=AllOptional):
    """An update to an existing data layer"""

    async def update(self, db_io: DbIO) -> LayerReadBase:
        layer_update_model = self.get_layer_type_plugin_class().get_layer_update_model()
        layer_update = self.ensure_model_type(layer_update_model)
        updated_id = await db_io.update("layers", layer_update)
        if not updated_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not update layer {updated_id}",
            )
        layer_read_model = self.get_layer_type_plugin_class().get_layer_read_model()
        updated_layer = layer_read_model(**await db_io.find_one("layers", updated_id))
        log.debug(f"Updated layer {updated_id}: {updated_layer.dict()}")
        return updated_layer
