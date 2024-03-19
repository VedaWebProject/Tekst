import asyncio
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache
from os.path import exists, realpath
from pathlib import Path
from urllib.parse import urljoin

from beanie.operators import Eq
from humps import decamelize

from tekst.config import TekstConfig, get_config
from tekst.logging import log
from tekst.models.email import TemplateIdentifier
from tekst.models.user import (
    UserDocument,
    UserRead,
)


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
_TEMPLATES_DIR = Path(realpath(__file__)).parent / "templates"


@lru_cache(maxsize=128)
def _get_email_templates(
    template_id: TemplateIdentifier, locale: str = "enUS"
) -> dict[str, str]:
    template_id = decamelize(template_id.value)
    templates = dict()
    for template_type in ("subject", "html", "txt"):
        path = _TEMPLATES_DIR / locale / f"{template_id}.{template_type}"
        if not exists(path) and locale != "enUS":  # pragma: no cover
            log.warning(
                "Missing email translation "
                f"'{template_id}.{template_type}' for locale '{locale}'. "
                "Falling back to 'enUS'."
            )
            path = _TEMPLATES_DIR / "enUS" / f"{template_id}.{template_type}"
        if not exists(path):  # pragma: no cover
            raise FileNotFoundError(f"{path} does not exist.")
        templates[template_type] = path.read_text(encoding="utf-8")
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
                **{f"to_user_{k}": v for k, v in to_user.model_dump().items()},
                **kwargs,
            )
            .strip()
        )
    _send_email(
        to=to_user.email,
        subject=email_contents.get("subject", ""),
        txt=email_contents.get("txt", ""),
        html=email_contents.get("html", ""),
    )


async def _broadcast_user_notification(
    template_id: TemplateIdentifier,
    **kwargs,
):
    for user in await UserDocument.find(
        Eq(UserDocument.user_notification_triggers, template_id.value),
        Eq(UserDocument.is_active, True),
        Eq(UserDocument.is_verified, True),
    ).to_list():
        await asyncio.sleep(1)
        send_email(
            to_user=user,
            template_id=template_id,
            **kwargs,
        )


async def broadcast_user_notification(
    template_id: TemplateIdentifier,
    **kwargs,
):
    asyncio.create_task(_broadcast_user_notification(template_id, **kwargs))


async def _broadcast_admin_notification(
    template_id: TemplateIdentifier,
    **kwargs,
):
    for admin in await UserDocument.find(
        Eq(UserDocument.is_superuser, True),
        Eq(UserDocument.admin_notification_triggers, template_id.value),
    ).to_list():
        await asyncio.sleep(1)
        send_email(
            to_user=admin,
            template_id=template_id,
            **kwargs,
        )


async def broadcast_admin_notification(
    template_id: TemplateIdentifier,
    **kwargs,
):
    asyncio.create_task(_broadcast_admin_notification(template_id, **kwargs))


def send_test_email(to_user: UserRead):
    send_email(to_user, TemplateIdentifier.TEST)
