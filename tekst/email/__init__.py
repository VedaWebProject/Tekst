import smtplib
from os.path import exists
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from functools import lru_cache
from glob import glob
from os.path import realpath
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


@lru_cache(maxsize=128)
def _get_templates(templateId: TemplateIdentifier, locale: str = "enUS") -> dict[str, str]:
    templates = dict()
    for template_type in ("subject", "html", "txt"):
        path = str(_TEMPLATES_DIR / locale / f"{templateId.value}.{template_type}")
        if not exists(path) and locale != "enUS":
            log.warning(
                "Missing email translation "
                f"'{templateId.value}.{template_type}' for locale '{locale}'. "
                "Falling back to 'enUS'."
            )
            path = str(_TEMPLATES_DIR / "enUS" / f"{templateId.value}.{template_type}")
        if not exists(path):
            raise FileNotFoundError(f"{path} does not exist.")
        with open(path, 'r') as fp:
            templates[template_type] = fp.read()
    return templates


def _send_email(*, to: str, subject: str, txt: str, html: str):
    log.debug(
        f"Sending mail to {to} via "
        f"{_cfg.email.smtp_server}:{_cfg.email.smtp_port}..."
    )
    msg = MIMEMultipart("alternative")
    msg["From"] = _cfg.email.from_address
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(txt, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(_cfg.email.smtp_server, _cfg.email.smtp_port) as smtp:
        if _cfg.email.smtp_starttls:
            log.debug("Initiating StartTLS handshake...")
            smtp.starttls()
        else:
            log.debug("Skipping StartTLS handshake, using unencrypted connection...")
        try:
            smtp.login(_cfg.email.smtp_user, _cfg.email.smtp_password)
            smtp.send_message(msg)
            log.debug("Email apparently sent successfully.")
        except Exception as e:
            log.error(
                f"Error sending email via "
                f"{_cfg.email.smtp_server}:{_cfg.email.smtp_port} "
                f"(StartTLS: {_cfg.email.smtp_starttls})"
            )
            raise e


def send_email(to_user: UserRead, templateId: TemplateIdentifier, **kwargs):
    templates = _get_templates(templateId, to_user.locale or "enUS")
    for key in templates:
        templates[key] = (
            templates[key]
            .format(
                web_url=urljoin(_cfg.server_url, _cfg.web_path).strip("/"),
                **_cfg.info.dict(by_alias=False),
                **to_user.dict(by_alias=False),
                **kwargs,
            )
            .strip()
        )
    _send_email(
        to=to_user.email,
        subject=templates.get("subject"),
        txt=templates.get("txt"),
        html=templates.get("html"),
    )


def send_test_email(to_user: UserRead):
    send_email(to_user, TemplateIdentifier.TEST)
