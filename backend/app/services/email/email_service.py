import html
import json
import logging
import re
import smtplib
from collections.abc import Callable
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any
from urllib.parse import quote

import resend

from app.core import config
from app.models.lead import Lead

logger = logging.getLogger(__name__)

EmailPayload = dict[str, Any]
_HEADER_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]+")

_TEMPLATES_DIR = Path(__file__).parent / "templates"
EMAIL_TEMPLATES = {
    file.stem: json.loads(file.read_text(encoding="utf-8"))
    for file in _TEMPLATES_DIR.glob("*.json")
}


def _safe_header(value: str) -> str:
    return " ".join(_HEADER_CONTROL_CHARACTERS.sub(" ", value).split())


def _format_submission_time(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    rendered = value.strftime("%B %d, %Y at %H:%M %Z").strip()
    return rendered.replace(" 0", " ")


class EmailConfigurationError(RuntimeError):
    """Raised when the selected email transport is not configured."""


class EmailService:
    def __init__(
        self,
        *,
        resend_api_key: str | None = None,
        email_from: str | None = None,
        attorney_email: str | None = None,
        attorney_emails: list[str] | str | None = None,
        frontend_url: str | None = None,
        email_backend: str | None = None,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
    ) -> None:
        self.resend_api_key = (
            config.RESEND_API_KEY if resend_api_key is None else resend_api_key
        )
        self.email_from = config.EMAIL_FROM if email_from is None else email_from

        if attorney_emails is not None:
            if isinstance(attorney_emails, str):
                self.attorney_emails = [e.strip() for e in attorney_emails.split(",") if e.strip()]
            else:
                self.attorney_emails = [e.strip() for e in attorney_emails if e.strip()]
        elif attorney_email is not None:
            self.attorney_emails = [attorney_email.strip()] if attorney_email.strip() else []
        else:
            raw_emails = config.ATTORNEY_EMAILS or config.ATTORNEY_EMAIL
            self.attorney_emails = [e.strip() for e in raw_emails.split(",") if e.strip()]

        self.attorney_email = self.attorney_emails[0] if self.attorney_emails else ""

        self.frontend_url = (
            config.FRONTEND_URL if frontend_url is None else frontend_url
        ).rstrip("/")
        self.email_backend = (
            config.EMAIL_BACKEND if email_backend is None else email_backend
        ).strip().lower()
        self.smtp_host = config.SMTP_HOST if smtp_host is None else smtp_host
        self.smtp_port = config.SMTP_PORT if smtp_port is None else smtp_port

    def send_prospect_confirmation(self, lead: Lead) -> None:
        self._deliver(self._prospect_payload(lead))

    def send_attorney_notification(self, lead: Lead) -> None:
        if not self.attorney_emails:
            raise EmailConfigurationError("ATTORNEY_EMAIL is not configured")
        self._deliver(self._attorney_payload(lead))

    def _prospect_payload(self, lead: Lead) -> EmailPayload:
        tmpl = EMAIL_TEMPLATES["prospect"]
        ref_number = lead.reference_number if getattr(lead, "reference_number", None) else ""
        ref_number_html = html.escape(ref_number, quote=True)

        ticket_ref_text = f"\nYour Ticket Reference: {ref_number}\n" if ref_number else ""
        ticket_ref_html = (
            f'<div style="background-color: #f3f4f6; border-radius: 6px; padding: 12px 16px; margin: 16px 0; border: 1px solid #e5e7eb;">'
            f'<p style="margin: 0; font-size: 13px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Your Ticket Reference</p>'
            f'<p style="margin: 4px 0 0 0; font-size: 18px; font-weight: bold; color: #111827; letter-spacing: 1px;">{ref_number_html}</p>'
            f'</div>'
            if ref_number
            else ""
        )

        ctx = {
            "first_name": lead.first_name,
            "first_name_html": html.escape(lead.first_name, quote=True),
            "ticket_ref_text": ticket_ref_text,
            "ticket_ref_html": ticket_ref_html,
        }

        return {
            "from": _safe_header(self.email_from),
            "to": [_safe_header(lead.email)],
            "subject": tmpl["subject"].format(**ctx),
            "text": tmpl["text"].format(**ctx),
            "html": tmpl["html"].format(**ctx),
        }

    def _attorney_payload(self, lead: Lead) -> EmailPayload:
        tmpl = EMAIL_TEMPLATES["attorney"]
        lead_url = self.lead_details_url(lead)
        submitted = _format_submission_time(lead.created_at)
        subject_name = _safe_header(f"{lead.first_name} {lead.last_name}")

        ctx = {
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "first_name_html": html.escape(lead.first_name, quote=True),
            "last_name_html": html.escape(lead.last_name, quote=True),
            "email": lead.email,
            "email_html": html.escape(lead.email, quote=True),
            "submitted": submitted,
            "submitted_html": html.escape(submitted, quote=True),
            "lead_url": lead_url,
            "lead_url_html": html.escape(lead_url, quote=True),
            "subject_name": subject_name,
        }

        recipients = (
            [_safe_header(e) for e in self.attorney_emails]
            if self.attorney_emails
            else [_safe_header(self.attorney_email)]
        )

        return {
            "from": _safe_header(self.email_from),
            "to": recipients,
            "subject": tmpl["subject"].format(**ctx),
            "text": tmpl["text"].format(**ctx),
            "html": tmpl["html"].format(**ctx),
        }

    def lead_details_url(self, lead: Lead) -> str:
        lead_id = quote(str(lead.id), safe="")
        return f"{self.frontend_url}/admin/leads/{lead_id}"

    def _deliver(self, payload: EmailPayload) -> None:
        if self.email_backend == "smtp":
            self._send_via_smtp(payload)
            return
        if self.email_backend == "preview":
            self._log_preview(payload)
            return
        if self.email_backend != "resend":
            raise EmailConfigurationError(
                f"Unsupported EMAIL_BACKEND: {self.email_backend}"
            )
        if not self.resend_api_key:
            self._log_preview(payload)
            return

        # TODO (Production - Resend Email Service):
        # 1. Set EMAIL_BACKEND=resend and provide RESEND_API_KEY in environment variables.
        # 2. Ensure EMAIL_FROM uses a domain verified in your Resend account (with SPF/DKIM).
        # 3. Add webhook endpoint (e.g. POST /api/webhooks/resend) to receive email delivery, bounce, and open events.
        # 4. Integrate a distributed background worker (e.g. Celery / AWS SQS) for resilient retry scheduling.
        resend.api_key = self.resend_api_key
        resend.Emails.send(payload)

    def _send_via_smtp(self, payload: EmailPayload) -> None:
        if not self.smtp_host:
            raise EmailConfigurationError(
                "SMTP_HOST is required when EMAIL_BACKEND=smtp"
            )

        message = EmailMessage()
        message["From"] = payload["from"]
        message["To"] = ", ".join(payload["to"])
        message["Subject"] = payload["subject"]
        message.set_content(payload["text"])
        message.add_alternative(payload["html"], subtype="html")

        with smtplib.SMTP(
            self.smtp_host,
            self.smtp_port,
            timeout=config.SMTP_TIMEOUT_SECONDS,
        ) as smtp:
            smtp.send_message(message)

    @staticmethod
    def _log_preview(payload: EmailPayload) -> None:
        logger.warning(
            "[DEV EMAIL - NOT DELIVERED] To: %s | Subject: %s",
            ", ".join(payload["to"]),
            payload["subject"],
        )


def get_email_service() -> EmailService:
    return EmailService()


def send_lead_emails_safely(email_service: EmailService, lead: Lead) -> None:
    _attempt_email(
        "prospect",
        lead,
        lambda: email_service.send_prospect_confirmation(lead),
    )
    _attempt_email(
        "attorney",
        lead,
        lambda: email_service.send_attorney_notification(lead),
    )


def _attempt_email(kind: str, lead: Lead, send: Callable[[], None]) -> None:
    try:
        send()
    except Exception as exc:
        # Do not include exception text: provider errors may contain credentials or
        # request headers. The error type and lead ID are sufficient for diagnostics.
        logger.error(
            "Failed to send %s email (%s)",
            kind,
            type(exc).__name__,
            extra={"lead_id": lead.id},
        )
