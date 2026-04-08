from enum import StrEnum
from typing import Annotated, Literal, get_args

from pydantic import Field


class Notification(StrEnum):
    EMAIL_TEST = "test"
    EMAIL_VERIFY = "verify"
    EMAIL_VERIFIED = "verified"
    EMAIL_USER_AWAITS_ACTIVATION = "userAwaitsActivation"
    EMAIL_ACTIVATED = "activated"
    EMAIL_DEACTIVATED = "deactivated"
    EMAIL_DELETED = "deleted"
    EMAIL_PASSWORD_FORGOT = "passwordForgot"
    EMAIL_PASSWORD_RESET = "passwordReset"
    EMAIL_SUPERUSER_SET = "superuserSet"
    EMAIL_SUPERUSER_UNSET = "superuserUnset"
    EMAIL_MESSAGE_RECEIVED = "messageReceived"
    EMAIL_NEW_CORRECTION = "newCorrection"
    EMAIL_ADDED_AS_OWNER = "addedAsOwner"
    USRMSG_RESOURCE_PROPOSED = "resourceProposed"
    USRMSG_RESOURCE_PUBLISHED = "resourcePublished"


type UserNotificationTrigger = Literal[
    Notification.EMAIL_MESSAGE_RECEIVED,
    Notification.EMAIL_NEW_CORRECTION,
    Notification.EMAIL_ADDED_AS_OWNER,
    Notification.USRMSG_RESOURCE_PROPOSED,
    Notification.USRMSG_RESOURCE_PUBLISHED,
]

type AdminNotificationTrigger = Literal[
    Notification.EMAIL_USER_AWAITS_ACTIVATION,
    Notification.EMAIL_NEW_CORRECTION,
]

UserNotificationTriggers = Annotated[
    list[UserNotificationTrigger],
    Field(
        description="Events that trigger notifications for this user",
        max_length=len(get_args(UserNotificationTrigger.__value__)),
    ),
]

AdminNotificationTriggers = Annotated[
    list[AdminNotificationTrigger],
    Field(
        description="Events that trigger admin notifications for this user",
        max_length=len(get_args(AdminNotificationTrigger.__value__)),
    ),
]
