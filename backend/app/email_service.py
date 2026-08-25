import html
import logging

import resend

from app.config import ATTORNEY_EMAIL, EMAIL_FROM, RESEND_API_KEY
from app.models import Lead

logger = logging.getLogger(__name__)

resend.api_key = RESEND_API_KEY

ATTORNEY_OFFICE_NAME = "Alma"


def _send(payload: dict) -> None:
    """Resend API call, isolated so tests can monkeypatch it instead of hitting
    the network, and so a missing key or an API error never bubbles up into
    the request that triggered it (this only ever runs as a background task)."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not set; skipping email (%s)", payload.get("subject"))
        return
    try:
        resend.api_key = RESEND_API_KEY
        resend.Emails.send(payload)
    except Exception:
        logger.exception("Failed to send email via Resend (%s)", payload.get("subject"))


def _prospect_email_payload(lead: Lead) -> dict:
    first_name = html.escape(lead.first_name)
    full_name = html.escape(f"{lead.first_name} {lead.last_name}")
    content = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
      <h2>Thanks for reaching out, {first_name}!</h2>
      <p>Hi {full_name},</p>
      <p>
        We've received your submission and a member of the {ATTORNEY_OFFICE_NAME}
        team will review your information and reach out shortly.
      </p>
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
    content = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
      <h2>New lead submitted — {ATTORNEY_OFFICE_NAME}</h2>
      <table cellpadding="4">
        <tr><td><strong>Name</strong></td><td>{full_name}</td></tr>
        <tr><td><strong>Email</strong></td><td>{email}</td></tr>
        <tr><td><strong>Status</strong></td><td>{lead.status.value}</td></tr>
        <tr><td><strong>Submitted</strong></td><td>{lead.created_at.isoformat()}</td></tr>
      </table>
      <p>Review this lead in the {ATTORNEY_OFFICE_NAME} dashboard.</p>
    </div>
    """
    return {
        "from": EMAIL_FROM,
        "to": [ATTORNEY_EMAIL],
        "subject": f"New lead: {lead.first_name} {lead.last_name}",
        "html": content,
    }


def send_lead_notifications(lead: Lead) -> None:
    """Runs as a FastAPI BackgroundTask after the lead-creation response has
    already been sent, so a slow or failing Resend call never delays it."""
    _send(_prospect_email_payload(lead))
    _send(_attorney_email_payload(lead))
