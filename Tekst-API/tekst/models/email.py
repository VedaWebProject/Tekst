from enum import Enum


class TemplateIdentifier(Enum):
    TEST = "test"
    VERIFY = "verify"
    VERIFIED = "verified"
    USER_AWAITS_ACTIVATION = "userAwaitsActivation"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"
    PASSWORD_FORGOT = "passwordForgot"
    PASSWORD_RESET = "passwordReset"
    SUPERUSER_SET = "superuserSet"
    SUPERUSER_UNSET = "superuserUnset"
    RESOURCE_PROPOSED = "resourceProposed"
    RESOURCE_PUBLISHED = "resourcePublished"
    MESSAGE_RECEIVED = "messageReceived"
