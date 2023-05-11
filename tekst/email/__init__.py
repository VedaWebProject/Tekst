import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import realpath
from pathlib import Path
from urllib.parse import urljoin

from tekst.config import TekstConfig, get_config
from tekst.email.templates import EMAIL_TEMPLATES, TemplateIdentifier
from tekst.logging import log
from tekst.models.user import UserRead


_cfg: TekstConfig = get_config()  # get (possibly cached) config data
_TEMPLATES_DIR = Path(realpath(__file__)).parent / "templates"


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
    templates = EMAIL_TEMPLATES.get(to_user.locale or "enUS").get(templateId.value)
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
