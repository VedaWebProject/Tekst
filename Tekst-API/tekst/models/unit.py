from typing import Annotated

from beanie import PydanticObjectId
from pydantic import Field, field_validator

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
)


class UnitBase(ModelBase, ModelFactoryMixin):
    """A base model for types of data units belonging to a certain resource"""

    resource_id: PydanticObjectId = Field(..., description="Resource ID")
    resource_type: Annotated[
        str,
        Field(description="A string identifying one of the available resource types"),
    ]
    node_id: PydanticObjectId = Field(..., description="Parent text node ID")
    comment: Annotated[
        str | None,
        Field(
            description="Plaintext, potentially multiline comment on this unit",
            max_length=1000,
        ),
    ] = None

    __template_fields: tuple[str] = ("comment",)

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type_name(cls, v):
        from tekst.resource_types import resource_types_mgr

        resource_type_names = resource_types_mgr.list_names()
        if v.lower() not in resource_type_names:
            raise ValueError(
                f"Given resource type ({v}) is not a valid "
                f"resource type name (one of {resource_type_names})."
            )
        return v.lower()

    @classmethod
    def get_template_fields(cls) -> tuple[str]:
        return cls.__template_fields + getattr(cls, "_template_fields", tuple())


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class UnitBaseDocument(UnitBase, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "units"
        is_root = True
        indexes = ["resource_id", "node_id"]


UnitBaseUpdate = UnitBase.update_model()
