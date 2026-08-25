import logging
import smtplib
from collections.abc import Callable
from email.message import EmailMessage
from urllib.parse import quote

import resend

from app.core import config
from app.models.lead import Lead
from app.templates._shared import EmailPayload
from app.templates.attorney_email import build_attorney_email
from app.templates.prospect_email import build_prospect_email

logger = logging.getLogger(__name__)


class EmailConfigurationError(RuntimeError):
    """Raised when the selected email transport is not configured."""


class EmailService:
    def __init__(
        self,
        *,
        resend_api_key: str | None = None,
        email_from: str | None = None,
        attorney_email: str | None = None,
        frontend_url: str | None = None,
        email_backend: str | None = None,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
    ) -> None:
        self.resend_api_key = (
            config.RESEND_API_KEY if resend_api_key is None else resend_api_key
        )
        self.email_from = config.EMAIL_FROM if email_from is None else email_from
        self.attorney_email = (
            config.ATTORNEY_EMAIL if attorney_email is None else attorney_email
        )
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
        if not self.attorney_email.strip():
            raise EmailConfigurationError("ATTORNEY_EMAIL is not configured")
        self._deliver(self._attorney_payload(lead))

    def _prospect_payload(self, lead: Lead) -> EmailPayload:
        return build_prospect_email(lead, email_from=self.email_from)

    def _attorney_payload(self, lead: Lead) -> EmailPayload:
        lead_url = self.lead_details_url(lead)
        return build_attorney_email(
            lead,
            email_from=self.email_from,
            attorney_email=self.attorney_email,
            lead_url=lead_url,
        )

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
