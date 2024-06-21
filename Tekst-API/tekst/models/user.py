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
from typing_extensions import TypeAliasType

from tekst.config import TekstConfig, get_config
from tekst.models.common import LocaleKey, ModelBase, ModelFactoryMixin
from tekst.models.notifications import TemplateIdentifier
from tekst.utils.validators import CleanupMultiline, CleanupOneline, EmptyStringToNone


_cfg: TekstConfig = get_config()

MaybePrivateUserField = TypeAliasType(
    "MaybePrivateUserField", Literal["name", "affiliation", "bio"]
)
MaybePrivateUserFields = TypeAliasType(
    "MaybePrivateUserFields",
    Annotated[
        list[MaybePrivateUserField],
        Field(
            description="Data fields set public by this user",
            max_length=len(get_args(MaybePrivateUserField.__value__)),
        ),
    ],
)


UserNotificationTrigger = TypeAliasType(
    "UserNotificationTrigger",
    Literal[
        TemplateIdentifier.EMAIL_MESSAGE_RECEIVED.value,
        TemplateIdentifier.EMAIL_NEW_CORRECTION.value,
        TemplateIdentifier.USRMSG_RESOURCE_PROPOSED.value,
        TemplateIdentifier.USRMSG_RESOURCE_PUBLISHED.value,
    ],
)
UserNotificationTriggers = Annotated[
    list[UserNotificationTrigger],
    Field(
        description="Events that trigger notifications for this user",
        max_length=len(get_args(UserNotificationTrigger.__value__)),
    ),
]

AdminNotificationTrigger = TypeAliasType(
    "AdminNotificationTrigger",
    Literal[
        TemplateIdentifier.EMAIL_USER_AWAITS_ACTIVATION.value,
        TemplateIdentifier.EMAIL_NEW_CORRECTION.value,
    ],
)
AdminNotificationTriggers = Annotated[
    list[AdminNotificationTrigger],
    Field(
        description="Events that trigger admin notifications for this user",
        max_length=len(get_args(AdminNotificationTrigger.__value__)),
    ),
]


class UserReadPublic(ModelBase):
    id: PydanticObjectId
    username: str
    name: str | None = None
    affiliation: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_active: bool
    is_superuser: bool
    public_fields: MaybePrivateUserFields

    @model_validator(mode="after")
    def model_postprocess(self):
        for pf in get_args(MaybePrivateUserField.__value__):
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
    name: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=64,
        ),
        CleanupOneline,
    ]
    affiliation: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=180,
        ),
        CleanupOneline,
    ]
    locale: LocaleKey | None = None
    avatar_url: Annotated[
        str | None,
        StringConstraints(
            max_length=1024,
        ),
        CleanupOneline,
        EmptyStringToNone,
    ] = None
    bio: Annotated[
        str | None,
        StringConstraints(
            max_length=2000,
        ),
        CleanupMultiline,
        EmptyStringToNone,
    ] = None
    public_fields: MaybePrivateUserFields = []
    user_notification_triggers: UserNotificationTriggers = list(
        get_args(UserNotificationTrigger.__value__)
    )
    admin_notification_triggers: AdminNotificationTriggers = list(
        get_args(AdminNotificationTrigger.__value__)
    )
    seen: bool | None = None


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

    is_active: bool = _cfg.security.users_active_by_default
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

    is_active: bool = _cfg.security.users_active_by_default


UserUpdate = User.update_model(schemas.BaseUserUpdate)


class UsersSearchResult(ModelBase):
    users: Annotated[
        list[UserRead],
        Field(
            description="Paginated users data",
        ),
    ] = []
    total: Annotated[
        int,
        Field(
            description="Total number of search hits",
        ),
    ] = 0


class PublicUsersSearchResult(ModelBase):
    users: Annotated[
        list[UserReadPublic],
        Field(
            description="Paginated public users data",
        ),
    ] = []
    total: Annotated[
        int,
        Field(
            description="Total number of search hits",
        ),
    ] = 0
