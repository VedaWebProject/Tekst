from typing import Annotated, TypedDict

from beanie import PydanticObjectId
from pydantic import Field, field_validator

from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.types import (
    ConStr,
    ConStrOrNone,
    ResourceTypeName,
    SchemaOptionalNonNullable,
)


class EditorsComment(TypedDict):
    by: ConStr(
        max_length=128,
        cleanup="oneline",
    )
    comment: ConStr(
        max_length=5000,
        cleanup="multiline",
    )


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
    authors_comment: Annotated[
        ConStrOrNone(
            max_length=50000,
            cleanup="multiline",
        ),
        Field(
            description="Potentially multiline comment by the original author",
        ),
    ] = None
    editors_comments: Annotated[
        list[EditorsComment] | None,
        Field(
            description="Potentially multiline comments / working notes editors",
            min_length=1,
            max_length=64,
        ),
        SchemaOptionalNonNullable,
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

    @field_validator(
        "editors_comments",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def pre_validate_editors_comments(cls, v) -> list | None:
        if v is None:
            return v
        if type(v) is not list:  # pragma: no cover
            return [v]
        if len(v) == 0:
            return None
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
