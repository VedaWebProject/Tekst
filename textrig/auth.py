import contextlib

from fastapi import APIRouter, Depends, FastAPI, Request
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
from fastapi_users_db_beanie import BeanieBaseUser, BeanieUserDatabase, ObjectIDIDMixin
from fastapi_users_db_beanie.access_token import (
    BeanieAccessTokenDatabase,
    BeanieBaseAccessToken,
)
from textrig.config import TextRigConfig, get_config
from textrig.logging import log
from textrig.models.common import ModelBase, PyObjectId


_cfg: TextRigConfig = get_config()


class User(ModelBase, BeanieBaseUser[PyObjectId]):
    is_active: bool = _cfg.dev_mode
    is_verified: bool = _cfg.dev_mode
    first_name: str
    last_name: str


class UserRead(ModelBase, schemas.BaseUser[PyObjectId]):
    id: PyObjectId
    is_active: bool = _cfg.dev_mode
    is_verified: bool = _cfg.dev_mode
    first_name: str
    last_name: str


class UserCreate(ModelBase, schemas.BaseUserCreate):
    is_active: bool = _cfg.dev_mode
    is_verified: bool = _cfg.dev_mode
    first_name: str
    last_name: str


class UserUpdate(ModelBase, schemas.BaseUserUpdate):
    is_active: bool = _cfg.dev_mode
    is_verified: bool = _cfg.dev_mode
    first_name: str | None
    last_name: str | None


class AccessToken(ModelBase, BeanieBaseAccessToken[PyObjectId]):
    pass


_cookie_transport = CookieTransport(
    cookie_name="textriguserauth",
    cookie_max_age=_cfg.security.cookie_lifetime,
    cookie_domain=_cfg.domain or None,
    cookie_path=_cfg.root_path or "/",
    cookie_secure=True,
    cookie_httponly=True,
    cookie_samesite="lax",
)


_bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


async def get_user_db():
    yield BeanieUserDatabase(User)


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
        token_audience="textrig:jwt",
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


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PyObjectId]):
    reset_password_token_secret = _cfg.security.secret
    verification_token_secret = _cfg.security.secret
    reset_password_token_lifetime_seconds = _cfg.security.reset_pw_token_lifetime
    verification_token_lifetime_seconds = _cfg.security.verification_token_lifetime
    reset_password_token_audience = "textrig:reset"
    verification_token_audience = "textrig:verify"

    async def on_after_register(self, user: User, request: Request | None = None):
        log.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        log.info(f"User {user.id} has forgotten their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        log.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )

    async def validate_password(
        self,
        password: str,
        user: UserCreate | User,
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters long"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail address"
            )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


_fastapi_users = FastAPIUsers[User, PyObjectId](
    get_user_manager,
    [_auth_backend_cookie, _auth_backend_jwt],
)


async def create_user(user: UserCreate):
    """Creates/registers a new user programmatically"""
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.create(user)
                log.debug(f"User created: {user}")
    except UserAlreadyExists:
        log.warning(f"User {user.email} already exists")


def setup_auth_routes(app: FastAPI) -> list[APIRouter]:
    # cookie auth
    app.include_router(
        _fastapi_users.get_auth_router(
            _auth_backend_cookie, requires_verification=not _cfg.dev_mode
        ),
        prefix="/auth/cookie",
        tags=["auth"],
        include_in_schema=_cfg.dev_mode,  # only during development
    )
    # jwt auth
    app.include_router(
        _fastapi_users.get_auth_router(
            _auth_backend_jwt, requires_verification=not _cfg.dev_mode
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
            UserRead, UserUpdate, requires_verification=not _cfg.dev_mode
        ),
        prefix="/users",
        tags=["users"],
    )


def _current_user(**kwargs) -> callable:
    """Returns auth dependencies for API routes (optional auth in dev mode)"""
    return _fastapi_users.current_user(
        optional=kwargs.pop("optional", False) or _cfg.dev_mode, **kwargs
    )


# prepare auth dependencies for API routes
dep_user_unverified = _current_user()
dep_user = _current_user(verified=True)
dep_user_active = _current_user(verified=True, active=True)
dep_superuser = _current_user(verified=True, active=True, superuser=True)
dep_user_unverified_optional = _current_user(optional=True)
dep_user_optional = _current_user(optional=True, verified=True)
dep_user_active_optional = _current_user(optional=True, verified=True, active=True)
dep_superuser_optional = _current_user(
    optional=True, verified=True, active=True, superuser=True
)
