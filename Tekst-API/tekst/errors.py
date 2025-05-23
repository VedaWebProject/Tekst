from typing import Any, Literal

from fastapi import HTTPException, status

from tekst.config import TekstConfig, get_config
from tekst.models.common import ModelBase
from tekst.types import ConStrOrNone


_cfg: TekstConfig = get_config()


class ErrorDetail(ModelBase):
    key: str
    msg: ConStrOrNone() = None
    values: dict[str, str | int | float | bool] | None = None


class TekstErrorModel(ModelBase):
    detail: ErrorDetail


class TekstHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: TekstErrorModel | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


def responses(
    errors: list[TekstHTTPException],
) -> dict[int, dict[Literal["model"], type[TekstErrorModel]]]:
    d = {}
    for error in errors:
        if error.status_code not in d:
            d[error.status_code] = {}
        d[error.status_code]["model"] = TekstErrorModel
    return d


def _error_instance(
    status_code: int,
    key: str,
    msg: str | None = None,
    values: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
):
    return TekstHTTPException(
        status_code=status_code,
        headers=headers,
        detail=TekstErrorModel(
            detail=ErrorDetail(
                key=key,
                msg=msg,
                values=values,
            )
        ),
    )


def update_values(
    exc: TekstHTTPException,
    values: dict[str, Any],
) -> TekstHTTPException:
    if "values" in exc.detail.detail:  # pragma: no cover
        exc.detail.detail.values.update(values)
    else:
        exc.detail.detail.values = values
    return exc


# PLATFORM API HTTP ERRORS DEFINED BELOW

E_401_UNAUTHORIZED = _error_instance(
    status_code=status.HTTP_401_UNAUTHORIZED,
    key="unauthorized",
    msg="Authentication required",
)

E_409_RESOURCES_LIMIT_REACHED = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="resourcesLimitReached",
    msg="Resources limit reached for this user",
    values={
        "limit": _cfg.misc.max_resources_per_user,
    },
)

E_404_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="notFound",
    msg="Whatever was requested could not be found",
)

E_404_RESOURCE_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="resourceNotFound",
    msg="The resource could not be found",
)

E_404_EXPORT_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="exportNotFound",
    msg="The requested export could not be found",
)

E_404_BOOKMARK_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="bookmarkNotFound",
    msg="The bookmark could not be found",
)

E_409_BOOKMARK_EXISTS = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="bookmarkExists",
    msg="A bookmark for this location already exists",
)

E_409_BOOKMARKS_LIMIT_REACHED = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="bookmarksLimitReached",
    msg="User cannot have more than 1000 bookmarks",
    values={
        "limit": 1000,
    },
)

E_404_LOCATION_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="locationNotFound",
    msg="The location could not be found",
)

E_404_TEXT_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="textNotFound",
    msg="The text could not be found",
)

E_400_RESOURCE_INVALID_LEVEL = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceInvalidLevel",
    msg="The level of the resource is invalid",
)

E_400_RESOURCE_VERSION_OF_VERSION = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceVersionOfVersion",
    msg="The resource is already a version of another resource",
)

E_400_INVALID_REQUEST_DATA = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="invalidRequestData",
    msg="The request data is invalid",
)

E_400_LOCATION_RANGE_INVALID = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="locationRangeInvalid",
    msg="The passed location range is invalid",
)

E_400_UNSUPPORTED_EXPORT_FORMAT = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="unsupportedExportFormat",
    msg="The requested export format is not supported by this type of resource",
)

E_400_RESOURCE_PUBLIC_DELETE = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourcePublicDelete",
    msg="Cannot delete a published resource",
)

E_400_RESOURCE_PROPOSED_DELETE = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceProposedDelete",
    msg="Cannot delete a proposed resource",
)

E_400_RESOURCE_PUBLIC_PROPOSED_TRANSFER = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourcePublishedProposedTransfer",
    msg="Resource is published or proposed for publication and cannot be deleted",
)

E_400_TARGET_USER_NON_EXISTENT = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="targetUserNonExistent",
    msg="Target user doesn't exist",
)

E_403_FORBIDDEN = _error_instance(
    status_code=status.HTTP_403_FORBIDDEN,
    key="forbidden",
    msg="You have no permission to perform this action",
)

E_400_RESOURCE_VERSION_PROPOSE = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceVersionPropose",
    msg="Cannot propose a resource version",
)

E_400_RESOURCE_PUBLISH_UNPROPOSED = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourcePublishUnproposed",
    msg="Cannot publish an unproposed resource",
)

E_400_RESOURCE_PROPOSE_PUBLIC = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceProposePublic",
    msg="Cannot propose a published resource",
)

E_400_RESOUCE_VERSION_PUBLISH = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceVersionPublish",
    msg="Cannot publish a resource version",
)

E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="uploadInvalidMimeTypeNotJson",
    msg="Invalid file MIME type (must be 'application/json')",
)

E_400_UPLOAD_INVALID_JSON = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="uploadInvalidJson",
    msg="Import data is not valid JSON",
)

E_422_UPLOAD_INVALID_DATA = _error_instance(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    key="uploadInvalidData",
    msg="Import data does not match schema",
)

E_400_IMPORT_ID_MISMATCH = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="importIdMismatch",
    msg="Import data ID does not match the ID in the request",
)

E_400_IMPORT_ID_NON_EXISTENT = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="importIdNonExistent",
    msg="An ID in the import data does not exist",
)

E_400_IMPORT_INVALID_CONTENT_DATA = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="importInvalidContentData",
    msg="Invalid content data in import data",
)

E_500_INTERNAL_SERVER_ERROR = _error_instance(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    key="internalServerError",
    msg="An internal server error occurred. How embarrassing :(",
)

E_503_SERVICE_UNAVAILABLE = _error_instance(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    key="serviceUnavailable",
    msg="The API is currently unavailable or some services are not ready.",
)

E_409_CONTENT_CONFLICT = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="contentConflict",
    msg="The properties of this content conflict with another content",
)

E_404_CONTENT_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="contentNotFound",
    msg="The requested content could not be found",
)

E_400_MESSAGE_TO_SELF = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="messageToSelf",
    msg="You're not supposed to send a message to yourself",
)

E_400_CONTENT_TYPE_MISMATCH = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="contentTypeMismatch",
    msg="Resource type doesn't match resource",
)

E_400_INVALID_TEXT = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="referencedInvalidText",
    msg="Text ID in in request data doesn't reference an existing text",
)

E_400_INVALID_LEVEL = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="locationInvalidLevel",
    msg=(
        "The level index passed is invalid or doesn't "
        "match the level of a referenced object"
    ),
)

E_404_USER_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="userNotFound",
    msg="The requested user could not be found",
)

E_404_SEGMENT_NOT_FOUND = _error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="segmentNotFound",
    msg="The requested segment could not be found",
)

E_409_SEGMENT_KEY_LOCALE_CONFLICT = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="segmentKeyLocaleConflict",
    msg="A segment with this key and language already exists",
)

E_409_TEXT_SAME_TITLE_OR_SLUG = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="textSameTitleOrSlug",
    msg="An equal text already exists (same title or slug)",
)

E_409_TEXT_IMPORT_LOCATIONS_EXIST = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="textImportLocationsExist",
    msg="Text already has locations",
)

E_400_TEXT_DELETE_LAST_TEXT = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="textDeleteLastText",
    msg="Cannot delete the last text",
)

E_409_ACTION_LOCKED = _error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="locked",
    msg="The operation cannot be executed right now because of an active lock",
)

E_400_REQUESTED_TOO_MANY_SEARCH_RESULTS = _error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="requestedTooManySearchResults",
    msg="Maximum number of requested search results exceeded: 10000",
)
