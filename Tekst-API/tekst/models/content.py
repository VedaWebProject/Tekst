from typing import Annotated

from beanie import PydanticObjectId
from pydantic import Field, StringConstraints, field_validator

from tekst.models.common import (
    DocumentBase,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.utils import validators as val


class ContentBase(ModelBase, ModelFactoryMixin):
    """A base model for types of contents belonging to a certain resource"""

    resource_id: PydanticObjectId = Field(..., description="Resource ID")
    resource_type: Annotated[
        str,
        Field(description="A string identifying one of the available resource types"),
    ]
    location_id: PydanticObjectId = Field(..., description="Parent text location ID")
    comment: Annotated[
        str | None,
        StringConstraints(max_length=50000, strip_whitespace=True),
        val.CleanupMultiline,
        val.EmtpyStringToNone,
        Field(
            description=(
                "Plain text, potentially multiline comment "
                "that will be displayed with the content"
            ),
        ),
    ] = None
    notes: Annotated[
        str | None,
        StringConstraints(max_length=1000, strip_whitespace=True),
        val.CleanupMultiline,
        val.EmtpyStringToNone,
        Field(
            description=(
                "Plain text, potentially multiline working notes on this content "
                "meant as an aid for people editing this content"
            ),
        ),
    ] = None

    @field_validator("resource_type", mode="after")
    @classmethod
    def validate_resource_type_name(cls, v):
        from tekst.resources import resource_types_mgr

        resource_type_names = resource_types_mgr.list_names()
        if v not in resource_type_names:  # pragma: no cover
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
        indexes = ["resource_id", "location_id"]


ContentBaseUpdate = ContentBase.update_model()
