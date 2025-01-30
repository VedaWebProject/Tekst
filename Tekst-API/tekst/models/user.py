from datetime import datetime
from typing import Annotated, Literal, get_args

from beanie import Document, PydanticObjectId
from fastapi_users import (
    schemas,
)
from fastapi_users_db_beanie import (
    BeanieBaseUser,
)
from pydantic import Field, model_validator
from pymongo import IndexModel
from typing_extensions import TypeAliasType

from tekst.config import TekstConfig, get_config
from tekst.i18n import LocaleKey
from tekst.models.common import (
    ModelBase,
    ModelFactoryMixin,
)
from tekst.models.notifications import TemplateIdentifier
from tekst.types import ConStr, ConStrOrNone, HttpUrlOrNone


_cfg: TekstConfig = get_config()

PrivateUserProp = TypeAliasType(
    "PrivateUserProp", Literal["name", "affiliation", "bio"]
)
PrivateUserProps = TypeAliasType(
    "PrivateUserProps",
    Annotated[
        list[PrivateUserProp],
        Field(
            description="Properties set to be private by this user",
            max_length=len(get_args(PrivateUserProp.__value__)),
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
    avatar_url: HttpUrlOrNone = None
    bio: str | None = None
    is_active: bool
    is_superuser: bool
    public_fields: PrivateUserProps

    @model_validator(mode="after")
    def model_postprocess(self):
        for pf in get_args(PrivateUserProp.__value__):
            if pf not in self.public_fields:
                setattr(self, pf, None)
        return self


class User(ModelBase, ModelFactoryMixin):
    """This base model defines the custom fields added to FastAPI-User's user model"""

    username: Annotated[
        ConStr(
            min_length=4,
            max_length=16,
            pattern=r"[a-zA-Z0-9\-_]+",
        ),
        Field(
            description="Public username of this user",
        ),
    ]
    name: Annotated[
        ConStr(
            max_length=64,
            cleanup="oneline",
        ),
        Field(
            description="Full name of this user",
        ),
    ]
    affiliation: Annotated[
        ConStr(
            max_length=180,
            cleanup="oneline",
        ),
        Field(
            description="Affiliation info of this user",
        ),
    ]
    locale: Annotated[
        LocaleKey | None,
        Field(
            description="Key of the locale used by this user",
        ),
    ] = None
    avatar_url: Annotated[
        HttpUrlOrNone,
        Field(
            description="URL of this user's avatar picture",
        ),
    ] = None
    bio: Annotated[
        ConStrOrNone(
            max_length=2000,
            cleanup="multiline",
        ),
        Field(
            description="Biography of this user",
        ),
    ] = None
    public_fields: PrivateUserProps = []
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
