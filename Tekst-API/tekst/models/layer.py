import re

from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import And, In, Or
from pydantic import (
    Field,
    StringConstraints,
    create_model,
    field_validator,
    model_validator,
)

from tekst.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    ModelFactoryMixin,
    TranslationBase,
    Translations,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserRead, UserReadPublic


class LayerDescriptionTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=512)
    ]


class LayerCommentTranslation(TranslationBase):
    translation: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)
    ]


class LayerBase(ModelBase, ModelFactoryMixin):
    """A data layer describing a set of data on a text"""

    title: Annotated[
        str, Field(min_length=1, max_length=64, description="Title of this layer")
    ]
    description: Annotated[
        Translations[LayerDescriptionTranslation],
        Field(
            description="Short, concise description of this data layer",
        ),
    ] = []
    text_id: Annotated[
        PydanticObjectId,
        Field(description="ID of the text this layer belongs to"),
    ]
    level: Annotated[int, Field(description="Text level this layer belongs to")]
    layer_type: Annotated[
        str, Field(description="A string identifying one of the available layer types")
    ]
    owner_id: Annotated[
        PydanticObjectId | None, Field(description="User owning this layer")
    ] = None
    category: Annotated[
        str | None,
        Field(description="Data layer category key", max_length=16),
    ] = None
    shared_read: Annotated[
        list[PydanticObjectId],
        Field(description="Users with shared read access to this layer"),
    ] = []
    shared_write: Annotated[
        list[PydanticObjectId],
        Field(description="Users with shared write access to this layer"),
    ] = []
    public: Annotated[
        bool, Field(description="Publication status of this layer")
    ] = False
    proposed: Annotated[
        bool, Field(description="Whether this layer has been proposed for publication")
    ] = False
    citation: Annotated[
        str | None,
        Field(description="Citation details for this layer", max_length=1000),
    ] = None
    meta: Metadata = []
    comment: Annotated[
        Translations[LayerCommentTranslation],
        Field(
            description="Plaintext, potentially multiline comment on this layer",
        ),
    ] = []

    @field_validator("description", mode="after")
    @classmethod
    def handle_whitespaces_in_description(cls, v):
        for desc_trans in v:
            desc_trans["translation"] = re.sub(
                r"[\s\n\r]+", " ", desc_trans["translation"]
            ).strip()
        return v

    @field_validator("layer_type")
    @classmethod
    def validate_layer_type_name(cls, v):
        from tekst.layer_types import layer_types_mgr

        layer_type_names = layer_types_mgr.list_names()
        if v.lower() not in layer_type_names:
            raise ValueError(
                f"Given layer type ({v}) is not a valid "
                f"layer type name (one of {layer_type_names})."
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

    @model_validator(mode="after")
    def model_postprocess(self):
        if self.public:
            # cannot be both public and proposed, public has priority
            self.proposed = False
            # published layers do not have an owner nor shares, only admins can edit
            self.owner_id = None
            self.shared_read = []
            self.shared_write = []
        # shares
        self.shared_write = [
            user_id for user_id in self.shared_write if user_id != self.owner_id
        ]
        self.shared_read = [
            user_id
            for user_id in self.shared_read
            if user_id != self.owner_id and user_id not in self.shared_write
        ]
        return self

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


class LayerBaseDocument(LayerBase, DocumentBase):
    class Settings(DocumentBase.Settings):
        name = "layers"
        is_root = True
        indexes = ["text_id", "level", "layer_type", "owner_id"]

    @classmethod
    async def allowed_to_read(cls, user: UserRead | None) -> dict:
        if not user:
            return {"public": True}
        if user.is_superuser:
            return {}

        active_texts_ids = [
            text.id
            for text in await TextDocument.find(
                TextDocument.is_active == True  # noqa: E712
            ).to_list()
        ]

        return And(
            Or(
                In(LayerBaseDocument.text_id, active_texts_ids),
                LayerBaseDocument.owner_id == user.id,
            ),
            Or(
                LayerBaseDocument.public == True,  # noqa: E712
                LayerBaseDocument.proposed == True,  # noqa: E712
                LayerBaseDocument.owner_id == user.id,
                LayerBaseDocument.shared_read == str(user.id),
                LayerBaseDocument.shared_write == str(user.id),
            ),
        )

    @classmethod
    def allowed_to_write(cls, user: UserRead | None) -> dict:
        if user.is_superuser:
            return {}
        uid = user.id if user else "no_id"
        return Or(
            LayerBaseDocument.owner_id == uid,
            LayerBaseDocument.shared_write == str(uid),
        )


class LayerReadExtras(ModelBase):
    writable: Annotated[
        bool | None,
        Field(description="Whether this layer is writable for the requesting user"),
    ] = None
    owner: Annotated[
        UserReadPublic | None,
        Field(
            description="Public user data for user owning this layer",
        ),
    ] = None
    shared_read_users: Annotated[
        list[UserReadPublic] | None,
        Field(
            description="Public user data for users allowed to read this layer",
        ),
    ] = None
    shared_write_users: Annotated[
        list[UserReadPublic] | None,
        Field(
            description="Public user data for users allowed to write this layer",
        ),
    ] = None


LayerBaseRead = create_model(
    "LayerBaseRead", __base__=(LayerBase.read_model(), LayerReadExtras)
)
LayerBaseUpdate = LayerBase.update_model()


class LayerNodeCoverage(ModelBase):
    label: str
    position: int
    covered: bool
