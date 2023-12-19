import contextlib
import re

from typing import Annotated, Any

import fastapi_users.models as fapi_users_models

from beanie import Document, PydanticObjectId
from beanie.operators import In, Pull
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    InvalidPasswordException,
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
    BeanieUserDatabase,
    ObjectIDIDMixin,
)
from fastapi_users_db_beanie.access_token import (
    BeanieAccessTokenDatabase,
    BeanieBaseAccessToken,
)
from humps import decamelize

from tekst.config import TekstConfig, get_config
from tekst.email import TemplateIdentifier, send_email
from tekst.logging import log
from tekst.models.resource import ResourceBaseDocument
from tekst.models.unit import UnitBaseDocument
from tekst.models.user import UserCreate, UserDocument, UserRead, UserUpdate


_cfg: TekstConfig = get_config()


class AccessToken(BeanieBaseAccessToken, Document):
    class Settings(BeanieBaseAccessToken.Settings):
        name = "access_tokens"


_cookie_transport = CookieTransport(
    cookie_name=_cfg.security_auth_cookie_name,
    cookie_max_age=_cfg.security_auth_cookie_lifetime or None,
    cookie_domain=_cfg.security_auth_cookie_domain or None,
    cookie_path=_cfg.api_path or "/",
    cookie_secure=not _cfg.dev_mode,
    cookie_httponly=True,
    cookie_samesite="Lax",
)

_bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


class CustomBeanieUserDatabase(BeanieUserDatabase):
    # This class is necessary to make our model logic work with FastAPI-Users :(

    async def create(self, create_dict: dict[str, Any]) -> UP_BEANIE:
        """Create a user."""
        return await super().create(decamelize(create_dict))

    async def update(self, user: UP_BEANIE, update_dict: dict[str, Any]) -> UP_BEANIE:
        """Update a user."""
        return await super().update(user, decamelize(update_dict))


async def get_user_db():
    yield CustomBeanieUserDatabase(UserDocument)


async def get_access_token_db():
    yield BeanieAccessTokenDatabase(AccessToken)


def _get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db, lifetime_seconds=_cfg.security_access_token_lifetime
    )


def _get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=_cfg.security_secret,
        lifetime_seconds=_cfg.security_auth_jwt_lifetime,
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


async def _get_enabled_backends() -> list[AuthenticationBackend]:
    """Returns the enabled backends following custom logic"""
    enabled_backends = []
    if _cfg.security_enable_cookie_auth:
        enabled_backends.append(_auth_backend_cookie)
    if _cfg.security_enable_jwt_auth:
        enabled_backends.append(_auth_backend_jwt)
    return enabled_backends


def _validate_required_password_chars(password: str):
    return (
        re.search(r"[a-z]", password)
        and re.search(r"[A-Z]", password)
        and re.search(r"[0-9]", password)
    )


class UserManager(ObjectIDIDMixin, BaseUserManager[UserDocument, PydanticObjectId]):
    reset_password_token_secret = _cfg.security_secret
    verification_token_secret = _cfg.security_secret
    reset_password_token_lifetime_seconds = _cfg.security_reset_pw_token_lifetime
    verification_token_lifetime_seconds = _cfg.security_verification_token_lifetime
    reset_password_token_audience = "tekst:reset"
    verification_token_audience = "tekst:verify"

    async def on_after_register(
        self, user: UserDocument, request: Request | None = None
    ):
        if not _cfg.security_users_active_by_default:
            admins = (
                await UserDocument.find(UserDocument.is_superuser == True)  # noqa: E712
                .limit(10)
                .to_list()
            )
            for admin in admins:
                send_email(
                    user,
                    TemplateIdentifier.ACTIVATE_TODO,
                    alternate_recepient=admin.email,
                )

    async def on_after_update(
        self,
        user: UserDocument,
        update_dict: dict[str, Any],
        request: Request | None = None,
    ):
        if "is_active" in update_dict:
            if update_dict.get("is_active"):
                send_email(user, TemplateIdentifier.ACTIVATED)
            else:
                send_email(user, TemplateIdentifier.DEACTIVATED)
        if "is_superuser" in update_dict:
            if update_dict.get("is_superuser"):
                send_email(user, TemplateIdentifier.SUPERUSER_SET)
            else:
                send_email(user, TemplateIdentifier.SUPERUSER_UNSET)
        if "password" in update_dict:
            send_email(
                user,
                TemplateIdentifier.PASSWORD_RESET,
            )

    async def on_after_login(
        self,
        user: UserDocument,
        request: Request | None = None,
        response: Response | None = None,
    ):
        pass  # nothing to do here ATM

    async def on_after_request_verify(
        self, user: UserDocument, token: str, request: Request | None = None
    ):
        send_email(
            user,
            TemplateIdentifier.VERIFY,
            token=token,
            token_lifetime_hours=int(
                _cfg.security_verification_token_lifetime / 60 / 60
            ),
        )

    async def on_after_verify(self, user: UserDocument, request: Request | None = None):
        send_email(user, TemplateIdentifier.VERIFIED)

    async def on_after_forgot_password(
        self, user: UserDocument, token: str, request: Request | None = None
    ):
        send_email(
            user,
            TemplateIdentifier.PASSWORD_FORGOT,
            token=token,
            token_lifetime_hours=int(_cfg.security_reset_pw_token_lifetime / 60 / 60),
        )

    async def on_after_reset_password(
        self, user: UserDocument, request: Request | None = None
    ):
        send_email(
            user,
            TemplateIdentifier.PASSWORD_RESET,
        )

    async def on_before_delete(
        self, user: UserDocument, request: Request | None = None
    ):
        # find owned resources
        resources_docs = await ResourceBaseDocument.find(
            ResourceBaseDocument.owner_id == user.id, with_children=True
        ).to_list()
        owned_resources_ids = [resource.id for resource in resources_docs]
        # delete units of owned resources
        await UnitBaseDocument.find(
            In(UnitBaseDocument.resource_id, owned_resources_ids),
            with_children=True,
        ).delete()
        # delete owned resources
        await ResourceBaseDocument.find_one(
            In(ResourceBaseDocument.id, owned_resources_ids),
            with_children=True,
        ).delete()
        # remove user ID from resource shares
        await ResourceBaseDocument.find(
            ResourceBaseDocument.shared_read == str(user.id),
            with_children=True,
        ).update(
            Pull(ResourceBaseDocument.shared_read == str(user.id)),
        )
        await ResourceBaseDocument.find(
            ResourceBaseDocument.shared_write == str(user.id),
            with_children=True,
        ).update(
            Pull(ResourceBaseDocument.shared_write == str(user.id)),
        )

    async def on_after_delete(self, user: UserDocument, request: Request | None = None):
        send_email(
            user,
            TemplateIdentifier.DELETED,
        )
        pass

    async def validate_password(
        self,
        password: str,
        user: UserCreate | UserDocument,
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
        existing_user = await UserDocument.find_one(
            UserDocument.username == user_create.username
        )
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="REGISTER_USERNAME_ALREADY_EXISTS",
            )
        return await super().create(user_create, **kwargs)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


_fastapi_users = FastAPIUsers[UserDocument, PydanticObjectId](
    get_user_manager,
    [_auth_backend_cookie, _auth_backend_jwt],
)


def setup_auth_routes(app: FastAPI) -> list[APIRouter]:
    # cookie auth
    if _cfg.security_enable_cookie_auth:
        app.include_router(
            _fastapi_users.get_auth_router(
                _auth_backend_cookie,
                requires_verification=not _cfg.security_closed_mode,
            ),
            prefix="/auth/cookie",
            tags=["auth"],
        )
    # jwt auth
    if _cfg.security_enable_jwt_auth:
        app.include_router(
            _fastapi_users.get_auth_router(
                _auth_backend_jwt,
                requires_verification=not _cfg.security_closed_mode,
            ),
            prefix="/auth/jwt",
            tags=["auth"],
        )
    # register
    app.include_router(
        _fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
        dependencies=[Depends(get_current_superuser)]
        if _cfg.security_closed_mode
        else [],
    )
    # verify
    if not _cfg.security_closed_mode:
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
            requires_verification=not _cfg.security_closed_mode,
        ),
        prefix="/users",
        tags=["users"],
    )


def _current_user(**kwargs) -> callable:
    """Returns auth dependencies for API routes (optional auth in dev mode)"""
    return _fastapi_users.current_user(
        optional=kwargs.pop("optional", False),
        get_enabled_backends=_get_enabled_backends,
        **kwargs,
    )


# auth dependencies for API routes
get_current_user = _current_user(verified=not _cfg.security_closed_mode, active=True)
get_current_superuser = _current_user(
    verified=not _cfg.security_closed_mode, active=True, superuser=True
)
get_current_optional_user = _current_user(
    verified=not _cfg.security_closed_mode, active=True, optional=True
)
UserDep = Annotated[UserRead, Depends(get_current_user)]
SuperuserDep = Annotated[UserRead, Depends(get_current_superuser)]
OptionalUserDep = Annotated[UserRead | None, Depends(get_current_optional_user)]


async def _create_user(user: UserCreate) -> UserRead:
    """
    Creates/registers a new user programmatically
    """
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
    try:
        async with get_user_db_context() as user_db:  # noqa: SIM117
            async with get_user_manager_context(user_db) as user_manager:
                return await user_manager.create(user, safe=False)
    except UserAlreadyExists:
        log.warning("User already exists. Skipping.")


async def create_initial_superuser():
    if _cfg.dev_mode:
        return
    # check if initial admin account is properly configured
    if not _cfg.security_init_admin_email or not _cfg.security_init_admin_password:
        log.warning("No initial admin account configured, skipping creation.")
        return
    # create inital admin account
    if await UserDocument.find_one(
        UserDocument.email == _cfg.security_init_admin_email
    ).exists():
        log.warning(
            f"Initial admin account for {_cfg.security_init_admin_email}"
            " already exists. Skipping creation."
        )
        return
    log.info("Creating initial admin account...")
    user = UserCreate(
        email=_cfg.security_init_admin_email,
        password=_cfg.security_init_admin_password,
        username="admin",
        name="Admin Admin",
        affiliation="Admin",
    )
    user.is_active = True
    user.is_verified = True
    user.is_superuser = True
    await _create_user(user)
    log.warning(
        f"Created initial admin account for email {_cfg.security_init_admin_email}. "
        "PLEASE CHANGE THIS ACCOUNT'S EMAIL AND PASSWORD IMMEDIATELY!"
    )


async def create_sample_users():
    """Creates sample users needed for testing in development"""
    if not _cfg.dev_mode:
        return
    log.debug("Creating sample users...")
    if await UserDocument.find_one().exists():
        log.warning("Users found in database. Skipping sample user creation.")
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
            name="Beth Smith",
            affiliation="Rick's daughter",
            is_verified=True,
            is_active=False,
            public_fields=["name", "affiliation"],
        )
    )
    # unverified user
    await _create_user(
        UserCreate(
            email=f"unverified{email_suffix}",
            username="jerr_unif",
            password=pw,
            name="Jerry Smith",
            affiliation="Rick's son-in-law",
            is_active=True,
            public_fields=["name", "affiliation"],
        )
    )
    # just a normal user, active and verified
    await _create_user(
        UserCreate(
            email=f"user{email_suffix}",
            username="the_morty123",
            password=pw,
            name="Morty Smith",
            affiliation="Rick's grandson",
            is_verified=True,
            is_active=True,
            public_fields=["name", "affiliation"],
        )
    )
    # superuser
    await _create_user(
        UserCreate(
            email=f"superuser{email_suffix}",
            username="SuperRick",
            password=pw,
            name="Rick Sanchez",
            affiliation="Mad scientist",
            is_verified=True,
            is_superuser=True,
            is_active=True,
            public_fields=["name", "affiliation"],
        )
    )
