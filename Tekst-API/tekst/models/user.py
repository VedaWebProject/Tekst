from datetime import datetime
from typing import Annotated, Literal, get_args

import pymongo

from beanie import Document, PydanticObjectId
from fastapi_users import (
    schemas,
)
from fastapi_users_db_beanie import (
    BeanieBaseUser,
)
from pydantic import Field, StringConstraints, model_validator
from pymongo import IndexModel

from tekst.config import TekstConfig, get_config
from tekst.models.common import LocaleKey, ModelBase, ModelFactoryMixin
from tekst.utils.validators import CleanupMultiline, CleanupOneline, EmptyStringToNone


_cfg: TekstConfig = get_config()

MaybePrivateUserFields = Literal["name", "affiliation", "bio"]
MaybePrivateUserFieldsType = Annotated[
    list[MaybePrivateUserFields],
    Field(description="Data fields set public by this user", max_length=64),
]


class UserReadPublic(ModelBase):
    id: PydanticObjectId
    username: str
    name: str | None = None
    affiliation: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_superuser: bool
    public_fields: MaybePrivateUserFieldsType = []

    @model_validator(mode="after")
    def model_postprocess(self):
        for pf in get_args(MaybePrivateUserFields):
            if pf not in self.public_fields:
                setattr(self, pf, None)
        return self


class User(ModelBase, ModelFactoryMixin):
    """This base model defines the custom fields added to FastAPI-User's user model"""

    username: Annotated[
        str,
        StringConstraints(
            min_length=4,
            max_length=16,
            pattern=r"[a-zA-Z0-9\-_]+",
            strip_whitespace=True,
        ),
    ]
    name: Annotated[str, StringConstraints(min_length=1, max_length=64), CleanupOneline]
    affiliation: Annotated[
        str, StringConstraints(min_length=1, max_length=180), CleanupOneline
    ]
    locale: LocaleKey | None = None
    avatar_url: Annotated[
        str | None,
        StringConstraints(max_length=1024),
        CleanupOneline,
        EmptyStringToNone,
    ] = None
    bio: Annotated[
        str | None,
        StringConstraints(max_length=2000),
        CleanupMultiline,
        EmptyStringToNone,
    ] = None
    public_fields: MaybePrivateUserFieldsType = []


class UserDocument(User, BeanieBaseUser, Document):
    """User document model used by FastAPI-Users"""

    class Settings(BeanieBaseUser.Settings):
        name = "users"
        indexes = BeanieBaseUser.Settings.indexes + [
            IndexModel("username", unique=True),
            IndexModel(
                [
                    ("username", pymongo.TEXT),
                    ("name", pymongo.TEXT),
                    ("affiliation", pymongo.TEXT),
                ],
            ),
        ]

    is_active: bool = _cfg.security_users_active_by_default
    created_at: datetime = datetime.utcnow()


class UserRead(User, schemas.BaseUser[PydanticObjectId]):
    """A user registered in the system"""

    # we redefine these fields here because they should be required in a read model
    # but have default values in FastAPI-User's schemas.BaseUser...
    id: PydanticObjectId
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime


class UserCreate(User, schemas.BaseUserCreate):
    """Dataset for creating a new user"""

    is_active: bool = _cfg.security_users_active_by_default


UserUpdate = User.update_model(schemas.BaseUserUpdate)
