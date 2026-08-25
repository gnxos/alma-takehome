import html
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import (
    ATTORNEY_EMAIL,
    EMAIL_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USERNAME,
)
from app.models.lead import Lead

logger = logging.getLogger(__name__)

ATTORNEY_OFFICE_NAME = "Alma"


def _build_message(payload: dict) -> MIMEMultipart:
    message = MIMEMultipart("alternative")
    message["From"] = payload["from"]
    message["To"] = ", ".join(payload["to"])
    message["Subject"] = payload["subject"]
    message.attach(MIMEText(payload["html"], "html"))
    return message


def _deliver(message: MIMEMultipart, recipients: list[str]) -> None:
    """SMTP call, isolated so tests can monkeypatch it instead of opening a
    real connection (to Mailpit or otherwise)."""
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as client:
        if SMTP_USE_TLS:
            client.starttls()
        if SMTP_USERNAME:
            client.login(SMTP_USERNAME, SMTP_PASSWORD)
        client.sendmail(message["From"], recipients, message.as_string())


def _send(payload: dict) -> bool:
    """Builds and delivers one email; isolated from send_lead_notifications
    so a slow/failing SMTP server never bubbles up into the request that
    triggered it (this only ever runs as a background task). Returns whether
    delivery succeeded, so the caller can persist that outcome."""
    try:
        _deliver(_build_message(payload), payload["to"])
        return True
    except Exception:
        logger.exception("Failed to send email via SMTP (%s)", payload.get("subject"))
        return False


def _prospect_email_payload(lead: Lead) -> dict:
    first_name = html.escape(lead.first_name)
    full_name = html.escape(f"{lead.first_name} {lead.last_name}")
    ref_number = html.escape(lead.reference_number) if getattr(lead, "reference_number", None) else ""
    ref_section = (
        f"""
      <div style="background-color: #f3f4f6; border-radius: 6px; padding: 12px 16px; margin: 16px 0; border: 1px solid #e5e7eb;">
        <p style="margin: 0; font-size: 13px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Your Ticket Reference</p>
        <p style="margin: 4px 0 0 0; font-size: 18px; font-weight: bold; color: #111827; letter-spacing: 1px;">{ref_number}</p>
      </div>
        """
        if ref_number
        else ""
    )
    content = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto; color: #1f2937; line-height: 1.5;">
      <h2>Thanks for reaching out, {first_name}!</h2>
      <p>Hi {full_name},</p>
      <p>
        We've received your submission and a member of the {ATTORNEY_OFFICE_NAME}
        team will review your information and reach out shortly.
      </p>
      {ref_section}
      <p>In the meantime, feel free to reply to this email with any questions.</p>
      <p>— The {ATTORNEY_OFFICE_NAME} Team</p>
    </div>
    """
    return {
        "from": EMAIL_FROM,
        "to": [lead.email],
        "subject": f"We've received your submission, {lead.first_name}!",
        "html": content,
    }


def _attorney_email_payload(lead: Lead) -> dict:
    full_name = html.escape(f"{lead.first_name} {lead.last_name}")
    email = html.escape(lead.email)
    
    extra_rows = []
    if getattr(lead, "phone", None):
        extra_rows.append(f"<tr><td><strong>Phone</strong></td><td>{html.escape(lead.phone)}</td></tr>")
    if getattr(lead, "message", None):
        extra_rows.append(f"<tr><td><strong>Message</strong></td><td>{html.escape(lead.message)}</td></tr>")
    extra_rows_html = "".join(extra_rows)
    
    content = f"""
    <div style="font-family: sans-serif; max-width: 520px; margin: 0 auto;">
      <h2>New lead submitted — {ATTORNEY_OFFICE_NAME}</h2>
      <table cellpadding="4" style="width: 100%; border-collapse: collapse;">
        <tr><td><strong>Name</strong></td><td>{full_name}</td></tr>
        <tr><td><strong>Email</strong></td><td>{email}</td></tr>
        <tr><td><strong>Reference</strong></td><td>{lead.reference_number}</td></tr>
        <tr><td><strong>Status</strong></td><td>{lead.status.value}</td></tr>
        {extra_rows_html}
        <tr><td><strong>Resume</strong></td><td>{html.escape(lead.resume_filename)}</td></tr>
        <tr><td><strong>Submitted</strong></td><td>{lead.created_at.isoformat() if lead.created_at else ''}</td></tr>
      </table>
      <p style="margin-top: 16px;">Review this lead in the {ATTORNEY_OFFICE_NAME} dashboard.</p>
    </div>
    """
    return {
        "from": EMAIL_FROM,
        "to": [ATTORNEY_EMAIL],
        "subject": f"New lead: {lead.first_name} {lead.last_name}",
        "html": content,
    }


def send_prospect_email(lead: Lead) -> bool:
    return _send(_prospect_email_payload(lead))


def send_attorney_email(lead: Lead) -> bool:
    return _send(_attorney_email_payload(lead))


def send_lead_notifications(lead: Lead) -> None:
    send_prospect_email(lead)
    send_attorney_email(lead)
