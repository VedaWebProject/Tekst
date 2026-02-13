from tekst.config import TekstConfig, get_config
from tekst.models.common import (
    ModelBase,
)


_cfg: TekstConfig = get_config()  # get (possibly cached) config data


class UserStats(ModelBase):
    contents: int
    locations: int
    resources: int
    texts: int
    users: int

    active_users_count_past_week: int
    active_users_count_past_month: int
    active_users_count_past_year: int

    search_quick: int
    search_advanced: int
    stats_requests: int


class SuperuserStats(UserStats):
    bookmarks: int
    corrections: int
    corrections_all_time: int
    emails: int
    messages: int
    messages_user: int
    logins: int
    active_sessions: int
    changed_passwords: int
    forgotten_passwords: int
    reset_passwords: int
    deleted_users: int
