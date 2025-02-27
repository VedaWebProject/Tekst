import asyncio
import smtplib

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache
from os.path import exists, realpath
from pathlib import Path
from urllib.parse import urljoin

from beanie.operators import Eq
from humps import decamelize

from tekst import tasks
from tekst.config import TekstConfig, get_config
from tekst.logs import log
from tekst.models.message import UserMessageDocument
from tekst.models.notifications import TemplateIdentifier
from tekst.models.user import (
    UserDocument,
    UserRead,
)
from tekst.state import get_state


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
_TEMPLATES_DIR = Path(realpath(__file__)).parent / "templates"


@lru_cache(maxsize=128)
def _get_notification_templates(
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
        f"{_cfg.email.smtp_server}:{_cfg.email.smtp_port}..."
    )
    msg = MIMEMultipart("alternative")
    msg["From"] = _cfg.email.from_address
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(txt, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(_cfg.email.smtp_server, _cfg.email.smtp_port) as smtp:
            if _cfg.email.smtp_starttls:
                log.debug("Initiating StartTLS handshake...")
                smtp.starttls()
            else:  # pragma: no cover
                log.debug(
                    "Skipping StartTLS handshake, using unencrypted connection..."
                )
            if _cfg.email.smtp_user and _cfg.email.smtp_password:  # pragma: no cover
                log.debug("Logging in to SMTP server...")
                smtp.login(_cfg.email.smtp_user, _cfg.email.smtp_password)
            smtp.send_message(msg)
            log.debug("Email apparently sent successfully.")
    except Exception as e:  # pragma: no cover
        log.error(
            f"Error sending email via "
            f"{_cfg.email.smtp_server}:{_cfg.email.smtp_port} "
            f"(StartTLS: {_cfg.email.smtp_starttls})"
        )
        log.error(e)


async def send_notification(
    to_user: UserRead,
    template_id: TemplateIdentifier,
    **kwargs,
):
    if not to_user or not template_id:  # pragma: no cover
        raise ValueError("Missing user or template ID.")
    templates = _get_notification_templates(template_id, to_user.locale or "enUS")
    msg_parts = dict()
    settings = await get_state()
    msg_attrs_platform = {"platform_name": settings.platform_name}
    msg_attrs_to_user = {f"to_user_{k}": v for k, v in to_user.model_dump().items()}
    for key in templates:
        msg_parts[key] = (
            templates[key]
            .format(
                web_url=urljoin(
                    str(_cfg.server_url),
                    _cfg.web_path,
                ).strip("/"),
                **msg_attrs_platform,
                **msg_attrs_to_user,
                **kwargs,
            )
            .strip()
        )
    # send
    if template_id.name.startswith("EMAIL_"):
        # send as email
        _send_email(
            to=to_user.email,
            subject=msg_parts.get("subject", ""),
            txt=msg_parts.get("txt", ""),
            html=msg_parts.get("html", ""),
        )
    elif template_id.name.startswith("USRMSG_"):
        # send as user message
        msg = f"{msg_parts.get('subject', '')}\n\n{msg_parts.get('txt', '')}"
        await UserMessageDocument(
            recipient=to_user.id,
            content=msg,
            created_at=datetime.utcnow(),
        ).create()


async def _broadcast_user_notification(
    template_id: TemplateIdentifier,
    **kwargs,
) -> None:
    if not template_id.name.startswith("USRMSG_"):  # pragma: no cover
        log.error(
            "Only user messages can be broadcasted to regular users "
            f"({template_id.name} is not a user message template!)."
        )
        return
    for user in await UserDocument.find(
        Eq(UserDocument.user_notification_triggers, template_id.value),
        Eq(UserDocument.is_active, True),
        Eq(UserDocument.is_verified, True),
    ).to_list():
        await send_notification(
            to_user=user,
            template_id=template_id,
            **kwargs,
        )


async def broadcast_user_notification(
    template_id: TemplateIdentifier,
    **kwargs,
):
    await tasks.create_task(
        _broadcast_user_notification,
        tasks.TaskType.BROADCAST_USER_NTFC,
        task_kwargs={
            "template_id": template_id,
            **kwargs,
        },
    )


async def _broadcast_admin_notification(
    template_id: TemplateIdentifier,
    **kwargs,
) -> None:
    for admin in await UserDocument.find(
        Eq(UserDocument.is_superuser, True),
        Eq(UserDocument.admin_notification_triggers, template_id.value),
    ).to_list():
        await asyncio.sleep(5)
        await send_notification(
            to_user=admin,
            template_id=template_id,
            **kwargs,
        )


async def broadcast_admin_notification(
    template_id: TemplateIdentifier,
    **kwargs,
):
    await tasks.create_task(
        _broadcast_admin_notification,
        tasks.TaskType.BROADCAST_ADMIN_NTFC,
        task_kwargs={
            "template_id": template_id,
            **kwargs,
        },
    )


async def send_test_email(to_user: UserRead):
    await send_notification(to_user, TemplateIdentifier.EMAIL_TEST)
