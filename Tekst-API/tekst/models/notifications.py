from enum import Enum


class TemplateIdentifier(Enum):
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
    USRMSG_RESOURCE_PROPOSED = "resourceProposed"
    USRMSG_RESOURCE_PUBLISHED = "resourcePublished"
