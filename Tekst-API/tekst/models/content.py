from typing import Annotated

from beanie import PydanticObjectId
from pydantic import Field, field_validator

from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.types import ConStrOrNone, ResourceTypeName


class ContentBase(ModelBase, ModelFactoryMixin):
    """A base model for types of contents belonging to a certain resource"""

    resource_id: Annotated[
        PydanticObjectId,
        Field(
            description="Resource ID",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
    ]
    resource_type: Annotated[
        ResourceTypeName,
        Field(
            description="A string identifying one of the available resource types",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
    ]
    location_id: Annotated[
        PydanticObjectId,
        Field(
            description="Text location ID",
        ),
        ExcludeFromModelVariants(
            update=True,
        ),
    ]
    comment: Annotated[
        ConStrOrNone(
            max_length=50000,
            cleanup="multiline",
        ),
        Field(
            description=(
                "Plain text, potentially multiline comment "
                "that will be displayed with the content"
            ),
        ),
    ] = None
    notes: Annotated[
        ConStrOrNone(
            max_length=1000,
            cleanup="multiline",
        ),
        Field(
            description=(
                "Plain text, potentially multiline working notes on this content "
                "meant as an aid for people editing this content"
            ),
        ),
    ] = None

    @field_validator(
        "resource_type",
        mode="after",
        check_fields=False,
    )
    @classmethod
    def validate_resource_type_name(cls, v):
        from tekst.resources import resource_types_mgr

        resource_type_names = resource_types_mgr.list_names()
        if v not in resource_type_names:
            raise ValueError(
                f"Given resource type ({v}) is not a valid "
                f"resource type name (one of {resource_type_names})."
            )
        return v


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class ContentBaseDocument(ContentBase, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "contents"
        is_root = True
        indexes = [
            "resource_id",
            "location_id",
        ]


ContentBaseUpdate = ContentBase.update_model()
