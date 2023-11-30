import re

from typing import Annotated

from beanie import PydanticObjectId
from beanie.operators import And, In, Or
from pydantic import Field, create_model, field_validator, model_validator

from tekst.models.common import (
    DocumentBase,
    Metadata,
    ModelBase,
    ModelFactoryMixin,
)
from tekst.models.text import TextDocument
from tekst.models.user import UserRead, UserReadPublic


class LayerBase(ModelBase, ModelFactoryMixin):
    """A data layer describing a set of data on a text"""

    title: Annotated[
        str, Field(min_length=1, max_length=64, description="Title of this layer")
    ]
    description: Annotated[
        str | None,
        Field(
            min_length=1,
            max_length=512,
            description="Short, concise description of this data layer",
        ),
    ] = None
    text_id: Annotated[
        PydanticObjectId | None,
        Field(description="ID of the text this layer belongs to"),
    ] = None
    level: Annotated[int, Field(description="Text level this layer belongs to")]
    layer_type: Annotated[
        str, Field(description="A string identifying one of the available layer types")
    ]
    owner_id: Annotated[
        PydanticObjectId | None, Field(description="User owning this layer")
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
    meta: Metadata = None
    comment: Annotated[
        str | None,
        Field(
            description="Plaintext, potentially multiline comment on this layer",
            max_length=1000,
        ),
    ] = None

    @field_validator("description")
    @classmethod
    def handle_whitespaces_in_description(cls, v):
        if not isinstance(v, str):
            return None
        return re.sub(r"[\s\n\r]+", " ", v).strip()

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

    @field_validator("comment")
    @classmethod
    def strip_comment_whitespaces(cls, v):
        if not isinstance(v, str):
            return None
        return re.sub(r"[\n\r]+", "\n", v).strip()

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
            Or(In(LayerBaseDocument.text_id, active_texts_ids), {"owner_id": user.id}),
            Or(
                {"public": True},
                {"proposed": True},
                {"owner_id": user.id},
                {"shared_read": user.id},
                {"shared_write": user.id},
            ),
        )

    @classmethod
    def allowed_to_write(cls, user: UserRead | None) -> dict:
        if user.is_superuser:
            return {}
        uid = user.id if user else "no_id"
        return Or(
            {"owner_id": uid},
            {"shared_write": uid},
        )

    class Settings(DocumentBase.Settings):
        name = "layers"
        is_root = True
        indexes = ["text_id", "level", "layer_type", "owner_id"]


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
