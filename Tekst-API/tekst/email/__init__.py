import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from functools import lru_cache
from os.path import exists, realpath
from pathlib import Path
from urllib.parse import urljoin

from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.user import UserRead


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
_TEMPLATES_DIR = Path(realpath(__file__)).parent / "templates"


class TemplateIdentifier(Enum):
    TEST = "test"
    VERIFY = "verify"
    VERIFIED = "verified"
    ACTIVATE_TODO = "activate_todo"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"
    PASSWORD_FORGOT = "password_forgot"
    PASSWORD_RESET = "password_reset"
    SUPERUSER_SET = "superuser_set"
    SUPERUSER_UNSET = "superuser_unset"


@lru_cache(maxsize=128)
def _get_email_templates(
    template_id: TemplateIdentifier, locale: str = "enUS"
) -> dict[str, str]:
    templates = dict()
    for template_type in ("subject", "html", "txt"):
        path = str(_TEMPLATES_DIR / locale / f"{template_id.value}.{template_type}")
        if not exists(path) and locale != "enUS":  # pragma: no cover
            log.warning(
                "Missing email translation "
                f"'{template_id.value}.{template_type}' for locale '{locale}'. "
                "Falling back to 'enUS'."
            )
            path = str(_TEMPLATES_DIR / "enUS" / f"{template_id.value}.{template_type}")
        if not exists(path):  # pragma: no cover
            raise FileNotFoundError(f"{path} does not exist.")
        with open(path) as fp:
            templates[template_type] = fp.read()
    return templates


def _send_email(*, to: str, subject: str, txt: str, html: str):
    log.debug(
        f"Sending mail to {to} via "
        f"{_cfg.email_smtp_server}:{_cfg.email_smtp_port}..."
    )
    msg = MIMEMultipart("alternative")
    msg["From"] = _cfg.email_from_address
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(txt, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(_cfg.email_smtp_server, _cfg.email_smtp_port) as smtp:
            if _cfg.email_smtp_starttls:
                log.debug("Initiating StartTLS handshake...")
                smtp.starttls()
            else:  # pragma: no cover
                log.debug(
                    "Skipping StartTLS handshake, using unencrypted connection..."
                )
            smtp.login(_cfg.email_smtp_user, _cfg.email_smtp_password)
            smtp.send_message(msg)
            log.debug("Email apparently sent successfully.")
    except Exception as e:  # pragma: no cover
        log.error(
            f"Error sending email via "
            f"{_cfg.email_smtp_server}:{_cfg.email_smtp_port} "
            f"(StartTLS: {_cfg.email_smtp_starttls})"
        )
        log.error(e)


def send_email(
    to_user: UserRead,
    template_id: TemplateIdentifier,
    *,
    alternate_recepient: UserRead | None = None,
    **kwargs,
):
    templates = _get_email_templates(template_id, to_user.locale or "enUS")
    email_contents = dict()
    for key in templates:
        email_contents[key] = (
            templates[key]
            .format(
                web_url=urljoin(str(_cfg.server_url), _cfg.web_path).strip("/"),
                **_cfg.model_dump(
                    include_keys_prefix="info_", strip_include_keys_prefix=True
                ),
                **to_user.model_dump(),
                **kwargs,
            )
            .strip()
        )
    _send_email(
        to=alternate_recepient or to_user.email,
        subject=email_contents.get("subject", ""),
        txt=email_contents.get("txt", ""),
        html=email_contents.get("html", ""),
    )


def send_test_email(to_user: UserRead):
    send_email(to_user, TemplateIdentifier.TEST)
