from typing import Any

from fastapi import HTTPException

from tekst.config import TekstConfig, get_config
from tekst.models.common import ModelBase


_cfg: TekstConfig = get_config()


class ErrorDetail(ModelBase):
    key: str
    msg: str | None = None
    values: dict[str, str | int | float | bool] | None = None


class TekstErrorModel(ModelBase):
    detail: ErrorDetail


class TekstHTTPException(HTTPException):
    detail: TekstErrorModel | None = None

    def __init__(
        self,
        status_code: int,
        detail: TekstErrorModel | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )


def responses(
    errors: list[TekstHTTPException],
) -> dict[int | str, dict[str, Any]]:
    d = {}
    for error in errors:
        if error.status_code not in d:
            d[error.status_code] = {}
        d[error.status_code]["model"] = TekstErrorModel
    return d


def err(
    status: int,
    key: str,
    *,
    msg: str | None = None,
    values: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
):
    return TekstHTTPException(
        status_code=status,
        headers=headers,
        detail=TekstErrorModel(
            detail=ErrorDetail(
                key=key,
                msg=msg,
                values=values,
            )
        ),
    )


def mod(
    err: TekstHTTPException,
    *,
    status: int | None = None,
    key: str | None = None,
    msg: str | None = None,
    values: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> TekstHTTPException:
    err.status_code = status if status is not None else err.status_code

    if err.detail and isinstance(err.detail, TekstErrorModel):
        detail = TekstErrorModel(
            detail=ErrorDetail(
                key=key or err.detail.detail.key,
                msg=msg or err.detail.detail.msg,
                values=(err.detail.detail.values or {}).update(values or {}),
            )
        )
    else:  # pragma: no cover
        if key is None:
            raise ValueError("Must declare error key if missing in error to modify.")
        detail = TekstErrorModel(
            detail=ErrorDetail(
                key=key,
                msg=msg,
                values=values,
            )
        )

    err.detail = detail
    err.headers = (dict(err.headers) if err.headers else {}).update(headers or {})
    return err


# PLATFORM API HTTP ERRORS DEFINED BELOW

E_401_UNAUTHORIZED = err(
    401,
    "unauthorized",
    msg="Authentication required",
)

E_409_RESOURCES_LIMIT_REACHED = err(
    409,
    "resourcesLimitReached",
    msg="Resources limit reached for this user",
    values={"limit": _cfg.misc.max_resources_per_user},
)

E_404_NOT_FOUND = err(
    404,
    "notFound",
    msg="Whatever was requested could not be found",
)

E_404_RESOURCE_NOT_FOUND = err(
    404,
    "resourceNotFound",
    msg="The resource could not be found",
)

E_404_FILE_NOT_FOUND = err(
    404,
    "fileNotFound",
    msg="The requested file could not be found",
)

E_404_BOOKMARK_NOT_FOUND = err(
    404,
    "bookmarkNotFound",
    msg="The bookmark could not be found",
)

E_409_BOOKMARK_EXISTS = err(
    409,
    "bookmarkExists",
    msg="A bookmark for this location already exists",
)

E_409_BOOKMARKS_LIMIT_REACHED = err(
    409,
    "bookmarksLimitReached",
    msg="User cannot have more than 1000 bookmarks",
    values={"limit": 1000},
)

E_404_LOCATION_NOT_FOUND = err(
    404,
    "locationNotFound",
    msg="The location could not be found",
)

E_404_TEXT_NOT_FOUND = err(
    404,
    "textNotFound",
    msg="The text could not be found",
)

E_400_RESOURCE_INVALID_LEVEL = err(
    400,
    "resourceInvalidLevel",
    msg="The level of the resource is invalid",
)

E_400_RESOURCE_PATCH_OF_PATCH = err(
    400,
    "resourcePatchOfPatch",
    msg="The resource is already a patch of another resource",
)

E_400_INVALID_REQUEST_DATA = err(
    400,
    "invalidRequestData",
    msg="The request data is invalid",
)

E_400_LOCATION_RANGE_INVALID = err(
    400,
    "locationRangeInvalid",
    msg="The passed location range is invalid",
)

E_400_UNSUPPORTED_EXPORT_FORMAT = err(
    400,
    "unsupportedExportFormat",
    msg="The requested export format is not supported by this type of resource",
)

E_400_RESOURCE_PUBLIC_DELETE = err(
    400,
    "resourcePublicDelete",
    msg="Cannot delete a published resource",
)

E_400_RESOURCE_PROPOSED_DELETE = err(
    400,
    "resourceProposedDelete",
    msg="Cannot delete a proposed resource",
)

E_403_RESOURCE_PUBLIC_INVALID_OWNER = err(
    403,
    "resourcePublicInvalidOwner",
    msg="Only superusers may set regular users as owners of public resources",
)

E_400_TARGET_USER_NON_EXISTENT = err(
    400,
    "targetUserNonExistent",
    msg="Target user doesn't exist",
)

E_403_FORBIDDEN = err(
    403,
    "forbidden",
    msg="You have no permission to perform this action",
)

E_400_RESOURCE_PATCH_PROPOSE = err(
    400,
    "resourcePatchPropose",
    msg="Cannot propose a resource patch",
)

E_400_RESOURCE_PUBLISH_UNPROPOSED = err(
    400,
    "resourcePublishUnproposed",
    msg="Cannot publish an unproposed resource",
)

E_400_RESOURCE_PROPOSE_PUBLIC = err(
    400,
    "resourceProposePublic",
    msg="Cannot propose a published resource",
)

E_400_RESOUCE_PATCH_PUBLISH = err(
    400,
    "resourcePatchPublish",
    msg="Cannot publish a resource patch",
)

E_400_UPLOAD_INVALID_MIME_TYPE = err(
    400,
    "uploadInvalidMimeType",
    msg="Invalid file MIME type",
)

E_400_UPLOAD_INVALID_JSON = err(
    400,
    "uploadInvalidJson",
    msg="Import data is not valid JSON",
)

E_422_UPLOAD_INVALID_DATA = err(
    422,
    "uploadInvalidData",
    msg="Import data does not match schema",
)

E_400_IMPORT_ID_MISMATCH = err(
    400,
    "importIdMismatch",
    msg="Import data ID does not match the ID in the request",
)

E_400_IMPORT_ID_NON_EXISTENT = err(
    400,
    "importIdNonExistent",
    msg="An ID in the import data does not exist",
)

E_400_IMPORT_INVALID_CONTENT_DATA = err(
    400,
    "importInvalidContentData",
    msg="Invalid content data in import data",
)

E_500_INTERNAL_SERVER_ERROR = err(
    500,
    "internalServerError",
    msg="An internal server error occurred. How embarrassing :(",
)

E_503_SERVICE_UNAVAILABLE = err(
    503,
    "serviceUnavailable",
    msg="The API is currently unavailable or some services are not ready.",
)

E_409_CONTENT_CONFLICT = err(
    409,
    "contentConflict",
    msg="The properties of this content conflict with another content",
)

E_404_CONTENT_NOT_FOUND = err(
    404,
    "contentNotFound",
    msg="The requested content could not be found",
)

E_400_MESSAGE_TO_SELF = err(
    400,
    "messageToSelf",
    msg="You're not supposed to send a message to yourself",
)

E_400_CONTENT_TYPE_MISMATCH = err(
    400,
    "contentTypeMismatch",
    msg="Resource type doesn't match resource",
)

E_400_INVALID_TEXT = err(
    400,
    "referencedInvalidText",
    msg="Text ID in in request data doesn't reference an existing text",
)

E_400_INVALID_LEVEL = err(
    400,
    "locationInvalidLevel",
    msg=(
        "The level index passed is invalid or doesn't "
        "match the level of a referenced object"
    ),
)

E_404_USER_NOT_FOUND = err(
    404,
    "userNotFound",
    msg="The requested user could not be found",
)

E_404_SEGMENT_NOT_FOUND = err(
    404,
    "segmentNotFound",
    msg="The requested segment could not be found",
)

E_409_SEGMENT_KEY_LOCALE_CONFLICT = err(
    409,
    "segmentKeyLocaleConflict",
    msg="A segment with this key and language already exists",
)

E_409_TEXT_SAME_TITLE_OR_SLUG = err(
    409,
    "textSameTitleOrSlug",
    msg="An equal text already exists (same title or slug)",
)

E_409_TEXT_IMPORT_LOCATIONS_EXIST = err(
    409,
    "textImportLocationsExist",
    msg="Text already has locations",
)

E_400_TEXT_DELETE_LAST_TEXT = err(
    400,
    "textDeleteLastText",
    msg="Cannot delete the last text",
)

E_409_ACTION_LOCKED = err(
    409,
    "locked",
    msg="The operation cannot be executed right now because of an active lock",
)

E_400_REQUESTED_TOO_MANY_SEARCH_RESULTS = err(
    400,
    "requestedTooManySearchResults",
    msg="Maximum number of requested search results exceeded: 10000",
)
