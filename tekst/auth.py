import contextlib
import re

from typing import Annotated, Any

import fastapi_users.models as fapi_users_models

from beanie import Document
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    InvalidPasswordException,
    schemas,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users_db_beanie import (
    UP_BEANIE,
    BeanieBaseUser,
    BeanieUserDatabase,
    ObjectIDIDMixin,
)
from fastapi_users_db_beanie.access_token import (
    BeanieAccessTokenDatabase,
    BeanieBaseAccessToken,
)
from humps import decamelize
from pydantic import constr
from pymongo import IndexModel

from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.common import AllOptionalMeta, ModelBase, PyObjectId


_cfg: TekstConfig = get_config()

# modify FastAPI-User's collection names
# BeanieBaseUser.Settings.name = "users"
# BeanieBaseAccessToken.Settings.name = "access_tokens"


class UserBase(ModelBase):
    """This base class defines the custom fields added to FastAPI-User's user model"""

    username: constr(min_length=4, max_length=16, regex=r"[a-zA-Z0-9\-\._]+")
    first_name: constr(min_length=1, max_length=32)
    last_name: constr(min_length=1, max_length=32)


class User(UserBase, BeanieBaseUser, Document):
    """User document model used by FastAPI-Users"""

    is_active: bool = _cfg.security.users_active_by_default

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


class UserCreate(UserBase, schemas.BaseUserCreate):
    """Dataset for creating a new user"""

    is_active: bool = _cfg.security.users_active_by_default


class UserUpdate(UserBase, schemas.BaseUserUpdate, metaclass=AllOptionalMeta):
    """Updates to a user registered in the system"""

    pass


class AccessToken(BeanieBaseAccessToken, Document):
    class Settings(BeanieBaseAccessToken.Settings):
        name = "access_tokens"


_cookie_transport = CookieTransport(
    cookie_name=_cfg.security.auth_cookie_name,
    cookie_max_age=_cfg.security.auth_cookie_lifetime or None,
    cookie_domain=_cfg.security.auth_cookie_domain or None,
    cookie_path=_cfg.api_path or "/",
    cookie_secure=not _cfg.dev_mode,
    cookie_httponly=True,
    cookie_samesite="Lax",
)

_bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


class CustomBeanieUserDatabase(BeanieUserDatabase):
    # This class is necessary to make our model logic work with FastAPI-Users :(
    async def update(self, user: UP_BEANIE, update_dict: dict[str, Any]) -> UP_BEANIE:
        """Update a user."""
        return await super().update(user, decamelize(update_dict))


async def get_user_db():
    yield CustomBeanieUserDatabase(User)


async def get_access_token_db():
    yield BeanieAccessTokenDatabase(AccessToken)


def _get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db, lifetime_seconds=_cfg.security.access_token_lifetime
    )


def _get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=_cfg.security.secret,
        lifetime_seconds=_cfg.security.jwt_lifetime,
        token_audience="tekst:jwt",
    )


_auth_backend_cookie = AuthenticationBackend(
    name="cookie",
    transport=_cookie_transport,
    get_strategy=_get_database_strategy,
)

_auth_backend_jwt = AuthenticationBackend(
    name="jwt",
    transport=_bearer_transport,
    get_strategy=_get_jwt_strategy,
)


def _validate_required_password_chars(password: str):
    return (
        re.search(r"[a-z]", password)
        and re.search(r"[A-Z]", password)
        and re.search(r"[0-9]", password)
    )


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PyObjectId]):
    reset_password_token_secret = _cfg.security.secret
    verification_token_secret = _cfg.security.secret
    reset_password_token_lifetime_seconds = _cfg.security.reset_pw_token_lifetime
    verification_token_lifetime_seconds = _cfg.security.verification_token_lifetime
    reset_password_token_audience = "tekst:reset"
    verification_token_audience = "tekst:verify"

    async def on_after_register(self, user: User, request: Request | None = None):
        log.debug(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        log.debug(f"User {user.id} has forgotten their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        log.debug(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )

    async def validate_password(
        self,
        password: str,
        user: UserCreate | User,
    ) -> None:
        # validate length
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters long"
            )
        # validate characters
        if not _validate_required_password_chars(password):
            raise InvalidPasswordException(
                reason="Password must contain at least one of each a-z, A-Z, 0-9"
            )
        # check if password contains email
        if user.email.lower() in password.lower():
            raise InvalidPasswordException(
                reason="Password should not contain e-mail address"
            )

    async def create(self, user_create, **kwargs) -> fapi_users_models.UP:
        """
        Overrides FastAPI-User's BaseUserManager's create method to check if the
        username already exists and respond with a meaningful HTTP exception.
        """
        existing_user = await User.find_one(User.username == user_create.username)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="REGISTER_USERNAME_ALREADY_EXISTS",
            )
        return await super().create(user_create, **kwargs)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


_fastapi_users = FastAPIUsers[User, PyObjectId](
    get_user_manager,
    [_auth_backend_cookie, _auth_backend_jwt],
)


def setup_auth_routes(app: FastAPI) -> list[APIRouter]:
    # cookie auth
    app.include_router(
        _fastapi_users.get_auth_router(
            _auth_backend_cookie,
            requires_verification=_cfg.security.users_need_verification,
        ),
        prefix="/auth/cookie",
        tags=["auth"],
        include_in_schema=_cfg.dev_mode,  # only during development
    )
    # jwt auth
    app.include_router(
        _fastapi_users.get_auth_router(
            _auth_backend_jwt,
            requires_verification=_cfg.security.users_need_verification,
        ),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    # register
    app.include_router(
        _fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    # verify
    app.include_router(
        _fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )
    # reset pw
    app.include_router(
        _fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    # users
    app.include_router(
        _fastapi_users.get_users_router(
            UserRead,
            UserUpdate,
            requires_verification=_cfg.security.users_need_verification,
        ),
        prefix="/users",
        tags=["users"],
    )


def _current_user(**kwargs) -> callable:
    """Returns auth dependencies for API routes (optional auth in dev mode)"""
    return _fastapi_users.current_user(optional=kwargs.pop("optional", False), **kwargs)


# auth dependencies for API routes
UserDep = Annotated[
    UserRead,
    Depends(_current_user(verified=_cfg.security.users_need_verification, active=True)),
]
SuperuserDep = Annotated[
    UserRead,
    Depends(
        _current_user(
            verified=_cfg.security.users_need_verification, active=True, superuser=True
        )
    ),
]
OptionalUserDep = Annotated[
    UserRead | None,
    Depends(
        _current_user(
            verified=_cfg.security.users_need_verification, active=True, optional=True
        )
    ),
]


async def _create_user(user: UserCreate) -> UserRead:
    """
    Creates/registers a new user programmatically
    """
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                return await user_manager.create(user, safe=False)
    except UserAlreadyExists:
        log.warning("User already exists. Skipping.")


async def create_initial_superuser(user: UserCreate):
    user.is_active = True
    user.is_verified = True
    user.is_superuser = True
    await _create_user(user)


async def create_sample_users():
    """Creates sample users needed for testing in development"""
    if not _cfg.dev_mode:
        return
    # common
    pw = "poiPOI098"
    email_suffix = "@test.com"
    # inactive user
    await _create_user(
        UserCreate(
            email=f"inactive{email_suffix}",
            username="beth123",
            password=pw,
            first_name="Beth",
            last_name="Smith",
            is_verified=True,
            is_active=False,
        )
    )
    # unverified user
    await _create_user(
        UserCreate(
            email=f"unverified{email_suffix}",
            username="jerr.unif",
            password=pw,
            first_name="Jerry",
            last_name="Smith",
            is_active=True,
        )
    )
    # just a normal user, active and verified
    await _create_user(
        UserCreate(
            email=f"user{email_suffix}",
            username="the_morty123",
            password=pw,
            first_name="Morty",
            last_name="Smith",
            is_verified=True,
            is_active=True,
        )
    )
    # superuser
    await _create_user(
        UserCreate(
            email=f"superuser{email_suffix}",
            username="SuperRick",
            password=pw,
            first_name="Rick",
            last_name="Sanchez",
            is_verified=True,
            is_superuser=True,
            is_active=True,
        )
    )
