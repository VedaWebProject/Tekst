from datetime import UTC, datetime
from typing import Annotated, Literal, NotRequired, TypedDict

from beanie import PydanticObjectId
from pydantic import (
    AwareDatetime,
    Field,
    StringConstraints,
    field_validator,
)

from tekst.models.common import (
    DocumentBase,
    ExcludeFromModelVariants,
    ModelBase,
    make_update_model,
)
from tekst.types import (
    FalsyToNone,
    MultiLineString,
    ResourceTypeName,
    SchemaOptionalNonNullable,
    SingleLineString,
)


class ContentComment(TypedDict):
    """A comment on a content"""

    by: NotRequired[
        Annotated[
            str | None,
            StringConstraints(min_length=1, max_length=128),
            SingleLineString,
            FalsyToNone,
        ]
    ]

    comment: Annotated[
        str,
        StringConstraints(min_length=1, max_length=5000),
        MultiLineString,
    ]


class ContentBase(ModelBase):
    """A base model for types of contents belonging to a certain resource"""

    resource_id: Annotated[
        PydanticObjectId,
        Field(description="Resource ID"),
        ExcludeFromModelVariants(update=True),
    ]

    resource_type: Annotated[
        ResourceTypeName,
        Field(description="A string identifying one of the available resource types"),
    ]

    location_id: Annotated[
        PydanticObjectId,
        Field(description="Text location ID"),
        ExcludeFromModelVariants(update=True),
    ]

    comments: Annotated[
        list[ContentComment] | None,
        Field(
            description="Potentially multiline comments on the content",
            min_length=1,
            max_length=64,
        ),
        FalsyToNone,
        SchemaOptionalNonNullable,
    ] = None

    created_at: Annotated[
        AwareDatetime,
        Field(
            description="Timestamp of the content creation",
            default_factory=lambda: datetime.now(UTC),
        ),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ]

    archived: Annotated[
        bool,
        Field(description="Whether the content is archived"),
        ExcludeFromModelVariants(
            create=True,
            update=True,
        ),
    ] = False

    # @field_validator("created_at", mode="before", check_fields=False)
    # @classmethod
    # def set_created_at(cls, _):
    #     return datetime.now(UTC)

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

    @classmethod
    def create_model[ModelTypeT: type[ContentBase]](cls: ModelTypeT) -> ModelTypeT:
        """Returns the CREATE model variant of this content type"""
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def read_model[ModelTypeT: type[ContentBase]](cls: ModelTypeT) -> ModelTypeT:
        """Returns the READ model variant of this content type"""
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def update_model[ModelTypeT: type[ContentBase]](cls: ModelTypeT) -> ModelTypeT:
        """Returns the UPDATE model variant of this content type"""
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    @classmethod
    def document_model[ModelTypeT: type[ContentBase]](cls: ModelTypeT) -> ModelTypeT:
        """Returns the Beanie Document model variant of this content type"""
        raise NotImplementedError(
            "This method must be implemented by subclasses."
        )  # pragma: no cover

    def comments_for_csv(self) -> str:
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


ContentBaseUpdate = make_update_model(ContentBase)


class MissingContent(ModelBase):
    """
    A model representing a missing content.
    """

    resource_id: PydanticObjectId
    resource_type: Literal["none"]
    location_id: PydanticObjectId


class ContentArchiveSignature(ModelBase):
    class Settings:
        projection = {
            "id": "$_id",
            "created_at": 1,
            "archived": 1,
        }

    id: PydanticObjectId
    created_at: AwareDatetime
    archived: bool
