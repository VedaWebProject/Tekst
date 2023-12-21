import re

from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import And, Eq, In, Or
from pydantic import (
    Field,
    StringConstraints,
    create_model,
    field_validator,
)

from tekst.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    ModelFactoryMixin,
    ResourceConfigBase,
    TranslationBase,
    Translations,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserRead, UserReadPublic


class ResourceDescriptionTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=512)
    ]


class ResourceCommentTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
    ]


class ResourceBase(ModelBase, ModelFactoryMixin):
    """A resource describing a set of data on a text"""

    title: Annotated[
        str, Field(min_length=1, max_length=64, description="Title of this resource")
    ]
    description: Annotated[
        Translations[ResourceDescriptionTranslation],
        Field(
            description="Short, concise description of this resource",
        ),
    ] = []
    text_id: Annotated[
        PydanticObjectId,
        Field(description="ID of the text this resource belongs to"),
    ]
    level: Annotated[int, Field(description="Text level this resource belongs to")]
    resource_type: Annotated[
        str,
        Field(description="A string identifying one of the available resource types"),
    ]
    owner_id: Annotated[
        PydanticObjectId | None, Field(description="User owning this resource")
    ] = None
    category: Annotated[
        str | None,
        Field(description="Resource category key", max_length=16),
    ] = None
    shared_read: Annotated[
        list[PydanticObjectId],
        Field(
            description="Users with shared read access to this resource", max_length=64
        ),
    ] = []
    shared_write: Annotated[
        list[PydanticObjectId],
        Field(
            description="Users with shared write access to this resource", max_length=64
        ),
    ] = []
    sort_order: Annotated[
        int,
        Field(description="Sort order for displaying this resource among others", ge=0),
    ] = 100
    public: Annotated[
        bool, Field(description="Publication status of this resource")
    ] = False
    proposed: Annotated[
        bool,
        Field(description="Whether this resource has been proposed for publication"),
    ] = False
    citation: Annotated[
        str | None,
        Field(description="Citation details for this resource", max_length=1000),
    ] = None
    meta: Metadata = []
    comment: Annotated[
        Translations[ResourceCommentTranslation],
        Field(
            description="Plaintext, potentially multiline comment on this resource",
        ),
    ] = []
    config: ResourceConfigBase = ResourceConfigBase()

    @field_validator("description", mode="after")
    @classmethod
    def handle_whitespaces_in_description(cls, v):
        for desc_trans in v:
            desc_trans["translation"] = re.sub(
                r"[\s\n\r]+", " ", desc_trans["translation"]
            ).strip()
        return v

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

    @field_validator("comment", mode="after")
    @classmethod
    def strip_comment_whitespaces(cls, v):
        for comment in v:
            comment["translation"] = re.sub(
                r"[\n\r]+", "\n", comment["translation"]
            ).strip()
        return v

    def restricted_fields(self, user: UserRead | None = None) -> set[str] | None:
        restrict_shares_info = user is None or (
            user.id != self.owner_id and not user.is_superuser
        )
        restrictions: dict[str, bool] = {
            "shared_read": restrict_shares_info,
            "shared_write": restrict_shares_info,
        }
        return {k for k, v in restrictions.items() if v}


# generate document and update models for this base model,
# as those have to be used as bases for inheriting model's document/update models


class ResourceBaseDocument(ResourceBase, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "resources"
        is_root = True
        indexes = ["text_id", "level", "resource_type", "owner_id"]

    @classmethod
    async def access_conditions_read(cls, user: UserRead | None) -> dict:
        active_texts_ids = await TextDocument.get_active_texts_ids()
        # compose access condition for different user types
        if not user:
            # not logged in, no user
            return And(
                ResourceBaseDocument.public == True,  # noqa: E712
                In(ResourceBaseDocument.text_id, active_texts_ids),
            )
        elif user.is_superuser:
            # superusers can read all resources
            return {}
        else:
            # logged in as regular user
            return And(
                In(ResourceBaseDocument.text_id, active_texts_ids),
                Or(
                    ResourceBaseDocument.owner_id == user.id,
                    Or(
                        ResourceBaseDocument.public == True,  # noqa: E712
                        ResourceBaseDocument.proposed == True,  # noqa: E712
                        ResourceBaseDocument.shared_read == str(user.id),
                        ResourceBaseDocument.shared_write == str(user.id),
                    ),
                ),
            )

    @classmethod
    async def access_conditions_write(cls, user: UserRead | None) -> dict:
        if not user:
            # not logged in, no user (don't match anything!)
            return Eq(ResourceBaseDocument.public, "THIS_WONT_MATCH")

        if user.is_superuser:
            # superusers can write all resources
            return {}

        active_texts_ids = await TextDocument.get_active_texts_ids()

        # compose conditions for logged in, regular users
        return And(
            In(ResourceBaseDocument.text_id, active_texts_ids),
            ResourceBaseDocument.public == False,  # noqa: E712
            ResourceBaseDocument.proposed == False,  # noqa: E712
            Or(
                ResourceBaseDocument.owner_id == user.id,
                ResourceBaseDocument.shared_write == str(user.id),
            ),
        )


class ResourceReadExtras(ModelBase):
    writable: Annotated[
        bool | None,
        Field(description="Whether this resource is writable for the requesting user"),
    ] = None
    owner: Annotated[
        UserReadPublic | None,
        Field(
            description="Public user data for user owning this resource",
        ),
    ] = None
    shared_read_users: Annotated[
        list[UserReadPublic] | None,
        Field(
            description="Public user data for users allowed to read this resource",
        ),
    ] = None
    shared_write_users: Annotated[
        list[UserReadPublic] | None,
        Field(
            description="Public user data for users allowed to write this resource",
        ),
    ] = None


ResourceBaseRead = create_model(
    "ResourceBaseRead", __base__=(ResourceBase.read_model(), ResourceReadExtras)
)
ResourceBaseUpdate = ResourceBase.update_model()


class ResourceNodeCoverage(ModelBase):
    label: str
    position: int
    covered: bool
