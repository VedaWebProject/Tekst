from typing import Any, Literal

from fastapi import HTTPException, status

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


def error_instance(
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


def update_values(exc: TekstHTTPException, values: dict[str, Any]):
    if "values" in exc.detail.detail:
        exc.detail.detail.values.update(values)
    else:
        exc.detail.detail.values = values
    return exc


# PLATFORM API HTTP ERRORS DEFINED BELOW

E_401_UNAUTHORIZED = error_instance(
    status_code=status.HTTP_401_UNAUTHORIZED,
    key="unauthorized",
    msg="Authentication required",
)

E_409_RESOURCES_LIMIT_REACHED = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="resourcesLimitReached",
    msg="Resources limit reached for this user",
    values={
        "limit": _cfg.limits_max_resources_per_user,
    },
)

E_404_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="notFound",
    msg="Whatever was requested could not be found",
)

E_404_RESOURCE_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="resourceNotFound",
    msg="The resource could not be found",
)

E_404_BOOKMARK_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="bookmarkNotFound",
    msg="The bookmark could not be found",
)

E_409_BOOKMARK_EXISTS = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="bookmarkExists",
    msg="A bookmark for this location already exists",
)

E_409_BOOKMARKS_LIMIT_REACHED = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="bookmarksLimitReached",
    msg="User cannot have more than 1000 bookmarks",
    values={
        "limit": 1000,
    },
)

E_404_LOCATION_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="locationNotFound",
    msg="The location could not be found",
)

E_404_TEXT_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="textNotFound",
    msg="The text could not be found",
)

E_400_RESOURCE_INVALID_LEVEL = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceInvalidLevel",
    msg="The level of the resource is invalid",
)

E_400_RESOURCE_VERSION_OF_VERSION = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceVersionOfVersion",
    msg="The resource is already a version of another resource",
)

E_400_SHARED_WITH_USER_NON_EXISTENT = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="sharedWithUserNonExistent",
    msg="Shared-with user doesn't exist",
)

E_400_RESOURCE_PUBLIC_DELETE = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourcePublicDelete",
    msg="Cannot delete a published resource",
)

E_400_RESOURCE_PROPOSED_DELETE = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceProposedDelete",
    msg="Cannot delete a proposed resource",
)

E_400_RESOURCE_PUBLIC_PROPOSED_TRANSFER = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourcePublishedProposedTransfer",
    msg="Resource is published or proposed for publication and cannot be deleted",
)

E_400_TARGET_USER_NON_EXISTENT = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="targetUserNonExistent",
    msg="Target user doesn't exist",
)

E_403_FORBIDDEN = error_instance(
    status_code=status.HTTP_403_FORBIDDEN,
    key="forbidden",
    msg="You have no permission to perform this action",
)

E_400_RESOURCE_VERSION_PROPOSE = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceVersionPropose",
    msg="Cannot propose a resource version",
)

E_400_RESOURCE_PUBLISH_UNPROPOSED = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourcePublishUnproposed",
    msg="Cannot publish an unproposed resource",
)

E_400_RESOURCE_PROPOSE_PUBLIC = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceProposePublic",
    msg="Cannot propose a published resource",
)

E_400_RESOUCE_VERSION_PUBLISH = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="resourceVersionPublish",
    msg="Cannot publish a resource version",
)

E_400_UPLOAD_INVALID_MIME_TYPE_NOT_JSON = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="uploadInvalidMimeTypeNotJson",
    msg="Invalid file MIME type (must be 'application/json')",
)

E_400_UPLOAD_INVALID_JSON = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="uploadInvalidJson",
    msg="Import data is not valid JSON",
)

E_400_IMPORT_ID_MISMATCH = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="importIdMismatch",
    msg="Import data ID does not match the ID in the request",
)

E_400_IMPORT_ID_NON_EXISTENT = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="importIdNonExistent",
    msg="An ID in the import data does not exist",
)

E_400_IMPORT_INVALID_CONTENT_DATA = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="importInvalidContentData",
    msg="Invalid content data in import data",
)

E_500_INTERNAL_SERVER_ERROR = error_instance(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    key="internalServerError",
    msg="An internal server error occurred. How embarrassing :(",
)

E_409_CONTENT_CONFLICT = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="contentConflict",
    msg="The properties of this content conflict with another content",
)

E_404_CONTENT_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="contentNotFound",
    msg="The requested content could not be found",
)

E_400_CONTENT_ID_MISMATCH = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="contentIdMismatch",
    msg="Referenced resource ID in updates doesn't match the one in target content",
)

E_400_MESSAGE_TO_SELF = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="messageToSelf",
    msg="You're not supposed to send a message to yourself",
)

E_400_CONTENT_TYPE_MISMATCH = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="contentTypeMismatch",
    msg="Referenced resource type in updates doesn't match the one in target content",
)

E_400_INVALID_TEXT = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="referencedInvalidText",
    msg="Text ID in in request data doesn't reference an existing text",
)

E_400_INVALID_LEVEL = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="locationInvalidLevel",
    msg="The level index passed does not exist in target text",
)

E_400_LOCATION_NO_LEVEL_NOR_PARENT = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="locationNoLevelNorParent",
    msg="Must have either 'level' or 'parentId' set",
)

E_400_LOCATION_CHILDREN_NO_PARENT_NOR_TEXT = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="locationChildrenNoParentNorText",
    msg="Must have either 'parentId' or 'textId' set",
)

E_404_USER_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="userNotFound",
    msg="The requested user could not be found",
)

E_404_SEGMENT_NOT_FOUND = error_instance(
    status_code=status.HTTP_404_NOT_FOUND,
    key="segmentNotFound",
    msg="The requested segment could not be found",
)

E_409_SEGMENT_KEY_LOCALE_CONFLICT = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="segmentKeyLocaleConflict",
    msg="A segment with this key and language already exists",
)

E_409_TEXT_SAME_TITLE_OR_SLUG = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="textSameTitleOrSlug",
    msg="An equal text already exists (same title or slug)",
)

E_409_TEXT_IMPORT_LOCATIONS_EXIST = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="textImportLocationsExist",
    msg="Text already has locations",
)

E_400_TEXT_DELETE_LAST_TEXT = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="textDeleteLastText",
    msg="Cannot delete the last text",
)

E_409_ACTION_LOCKED = error_instance(
    status_code=status.HTTP_409_CONFLICT,
    key="locked",
    msg="The operation cannot be executed right now because of an active lock",
)

E_400_REQUESTED_TOO_MANY_SEARCH_RESULTS = error_instance(
    status_code=status.HTTP_400_BAD_REQUEST,
    key="requestedTooManySearchResults",
    msg="Maximum number of requested search results exceeded: 10000",
)
