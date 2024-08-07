import re

from typing import Annotated, Literal

from beanie import PydanticObjectId
from beanie.operators import And, Eq, In, Or
from pydantic import (
    Field,
    StringConstraints,
    field_validator,
)

from tekst.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    ModelFactoryMixin,
    TranslationBase,
    Translations,
)
from tekst.models.resource_configs import ResourceConfigBase
from tekst.models.text import TextDocument
from tekst.models.user import UserRead, UserReadPublic
from tekst.utils import validators as val
from tekst.utils.strings import cleanup_spaces_multiline


class ResourceTitleTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=64,
            strip_whitespace=True,
        ),
    ]


class ResourceDescriptionTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=512,
            strip_whitespace=True,
        ),
    ]


class ResourceCommentTranslation(TranslationBase):
    translation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=2000,
            strip_whitespace=True,
        ),
    ]


class ResourceBase(ModelBase, ModelFactoryMixin):
    """A resource describing a set of data on a text"""

    title: Annotated[
        Translations[ResourceTitleTranslation],
        Field(
            description="Title of this resource",
            min_length=1,
        ),
    ]
    description: Annotated[
        Translations[ResourceDescriptionTranslation],
        Field(
            description="Short, concise description of this resource",
        ),
    ] = []
    text_id: Annotated[
        PydanticObjectId,
        Field(
            description="ID of the text this resource belongs to",
        ),
    ]
    level: Annotated[
        int,
        Field(
            ge=0,
            description="Text level this resource belongs to",
        ),
    ]
    resource_type: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=32,
            strip_whitespace=True,
        ),
        Field(
            description="A string identifying one of the available resource types",
        ),
    ]
    original_id: Annotated[
        PydanticObjectId | None,
        Field(
            description=(
                "If this is a version of another resource,"
                " this ID references the original"
            ),
        ),
    ] = None
    owner_id: Annotated[
        PydanticObjectId | None,
        Field(
            description="User owning this resource",
        ),
    ] = None
    shared_read: Annotated[
        list[PydanticObjectId],
        Field(
            description="Users with shared read access to this resource",
            max_length=64,
        ),
    ] = []
    shared_write: Annotated[
        list[PydanticObjectId],
        Field(
            description="Users with shared write access to this resource",
            max_length=64,
        ),
    ] = []
    public: Annotated[
        bool,
        Field(
            description="Publication status of this resource",
        ),
    ] = False
    proposed: Annotated[
        bool,
        Field(
            description="Whether this resource has been proposed for publication",
        ),
    ] = False
    citation: Annotated[
        str | None,
        StringConstraints(
            max_length=1000,
        ),
        val.CleanupOneline,
        val.EmptyStringToNone,
        Field(
            description="Citation details for this resource",
        ),
    ] = None
    meta: Metadata = []
    comment: Annotated[
        Translations[ResourceCommentTranslation],
        Field(
            description="Plain text, potentially multiline comment on this resource",
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

    @field_validator("resource_type", mode="after")
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

    @field_validator("comment", mode="after")
    @classmethod
    def format_comment(cls, v):
        for comment in v:
            comment["translation"] = cleanup_spaces_multiline(comment["translation"])
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
        indexes = [
            "text_id",
            "level",
            "resource_type",
            "owner_id",
        ]

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
                        ResourceBaseDocument.shared_read == user.id,
                        ResourceBaseDocument.shared_write == user.id,
                    ),
                ),
            )

    @classmethod
    async def access_conditions_write(cls, user: UserRead | None) -> dict:
        if not user:  # pragma: no cover (as this should never happen anyway)
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
                ResourceBaseDocument.shared_write == user.id,
            ),
        )

    @classmethod
    async def user_resource_count(cls, user_id: PydanticObjectId | None) -> int:
        if not user_id:
            return 0  # pragma: no cover
        return await ResourceBaseDocument.find(
            ResourceBaseDocument.owner_id == user_id,
            with_children=True,
        ).count()


class ResourceReadExtras(ModelBase):
    writable: Annotated[
        bool | None,
        Field(
            description="Whether this resource is writable for the requesting user",
        ),
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


ResourceBaseUpdate = ResourceBase.update_model()


class ResourceCoverage(ModelBase):
    covered: int
    total: int


class ResourceLocationCoverage(ModelBase):
    label: str
    position: int
    covered: bool = False


class ResourceCoverageDetails(ModelBase):
    parent_labels: list[str]
    locations_coverage: list[list[ResourceLocationCoverage]]


ResourceExportFormat = Literal["json", "tekst-json", "csv", "txt", "html"]

res_exp_fmt_info = {
    "json": {
        "extension": "json",
        "mimetype": "application/json",
    },
    "tekst-json": {
        "extension": "json",
        "mimetype": "application/json",
    },
    "csv": {
        "extension": "csv",
        "mimetype": "text/csv",
    },
    "txt": {
        "extension": "txt",
        "mimetype": "text/plain",
    },
    "html": {
        "extension": "html",
        "mimetype": "text/html",
    },
}


class ResourceImportData(ModelBase):
    resource_id: PydanticObjectId
    contents: list[dict] = []
