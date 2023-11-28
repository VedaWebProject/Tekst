from typing import Annotated

from beanie import PydanticObjectId
from pydantic import Field

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
)


class UnitBase(ModelBase, ModelFactoryMixin):
    """A base model for types of data units belonging to a certain data layer"""

    layer_id: PydanticObjectId = Field(..., description="Data layer ID")
    node_id: PydanticObjectId = Field(..., description="Parent text node ID")
    comment: Annotated[
        str | None,
        Field(
            description="Plaintext, potentially multiline comment on this unit",
            max_length=1000,
        ),
    ] = None

    __template_fields: tuple[str] = ("comment",)

    @classmethod
    def get_template_fields(cls) -> tuple[str]:
        return cls.__template_fields + getattr(cls, "_template_fields", tuple())


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class UnitBaseDocument(UnitBase, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "units"
        is_root = True
        indexes = ["layer_id", "node_id"]


UnitBaseUpdate = UnitBase.update_model()
