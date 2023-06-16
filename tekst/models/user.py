from datetime import datetime
from typing import Literal

from beanie import Document
from fastapi_users import (
    schemas,
)
from fastapi_users_db_beanie import (
    BeanieBaseUser,
)
from humps import camelize
from pydantic import Field, constr
from pymongo import IndexModel

from tekst.config import TekstConfig, get_config
from tekst.models.common import AllOptionalMeta, Locale, ModelBase, PyObjectId


_cfg: TekstConfig = get_config()


class UserReadPublic(ModelBase):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    affiliation: str | None = None


PublicUserField = Literal[
    tuple(
        [
            camelize(field)
            for field in UserReadPublic.__fields__.keys()
            if field != "username"
        ]
    )
]


class UserBase(ModelBase):
    """This base model defines the custom fields added to FastAPI-User's user model"""

    username: constr(min_length=4, max_length=16, regex=r"[a-zA-Z0-9\-_]+")
    first_name: constr(min_length=1, max_length=32)
    last_name: constr(min_length=1, max_length=32)
    affiliation: constr(min_length=1, max_length=64)
    locale: Locale | None = None
    public_fields: list[PublicUserField] = Field(
        [], description="Data fields set public by this user"
    )


class User(UserBase, BeanieBaseUser, Document):
    """User document model used by FastAPI-Users"""

    is_active: bool = _cfg.security.users_active_by_default
    created_at: datetime = datetime.utcnow()

    class Settings(BeanieBaseUser.Settings):
        name = "users"
        indexes = BeanieBaseUser.Settings.indexes + [
            IndexModel("username", unique=True)
        ]


class UserRead(UserBase, schemas.BaseUser[PyObjectId]):
    """A user registered in the system"""

    # we redefine these fields here because they should be required in a read model
    # but have default values in FastAPI-User's schemas.BaseUser...
    id: PyObjectId
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime


class UserCreate(UserBase, schemas.BaseUserCreate):
    """Dataset for creating a new user"""

    is_active: bool = _cfg.security.users_active_by_default


class UserUpdate(UserBase, schemas.BaseUserUpdate, metaclass=AllOptionalMeta):
    """Updates to a user registered in the system"""

    pass
