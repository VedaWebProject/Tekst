from datetime import UTC, datetime
from typing import Annotated, Literal, NotRequired, TypedDict

from beanie import PydanticObjectId
from pydantic import AwareDatetime, BeforeValidator, Field, field_validator

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


class ContentComment(TypedDict):
    """A comment on a content"""

    by: NotRequired[
        ConStrOrNone(
            max_length=128,
            cleanup="oneline",
        )
    ]

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

    comments: Annotated[
        list[ContentComment] | None,
        Field(
            description="Potentially multiline comments on the content",
            min_length=1,
            max_length=64,
        ),
        BeforeValidator(lambda v: v or None),
        SchemaOptionalNonNullable,
    ] = None

    created_at: Annotated[
        AwareDatetime,
        Field(
            description="Timestamp of the content creation",
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ] = datetime.now(UTC)

    archived: Annotated[
        bool,
        Field(
            description="Whether the content is archived",
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ] = False

    @field_validator("resource_type", mode="after", check_fields=False)
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

    async def comments_for_csv(
        self,
    ) -> str:
        if not self.comments:
            return ""
        return "\n\n".join(
            [
                (
                    cmt["comment"]
                    if not cmt.get("by")
                    else f"{cmt['comment']}\n::comment by: {cmt['by']}::"
                )
                for cmt in self.comments
            ]
        )


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class ContentBaseDocument(ContentBase, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "contents"
        is_root = True
        indexes = [
            [
                "resource_id",
                "location_id",
                "created_at",
                "archived",
            ]
        ]

    async def archive(self) -> "ContentBaseDocument":
        """
        Archives this content and returns an unsaved copy (without ID) with an updated
        `created_at` datetime value set to now (UTC).
        """
        copy = self.model_copy(deep=True, update={"created_at": datetime.now(UTC)})
        copy.id = None
        self.archived = True
        await self.replace()
        return copy


ContentBaseUpdate = ContentBase.update_model()


class MissingContent(ModelBase):
    """
    A model representing a missing content.
    """

    resource_id: PydanticObjectId
    resource_type: Literal["none"]
    location_id: PydanticObjectId
