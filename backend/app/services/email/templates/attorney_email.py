import html

from app.models.lead import Lead
from ._shared import (
    EmailPayload,
    format_submission_time,
    safe_header,
)


def build_attorney_email(
    lead: Lead,
    *,
    email_from: str,
    attorney_email: str,
    lead_url: str,
) -> EmailPayload:
    first_name = html.escape(lead.first_name, quote=True)
    last_name = html.escape(lead.last_name, quote=True)
    prospect_email = html.escape(lead.email, quote=True)
    subject_name = safe_header(f"{lead.first_name} {lead.last_name}")
    submitted = format_submission_time(lead.created_at)
    escaped_url = html.escape(lead_url, quote=True)
    text = (
        "A new lead was submitted.\n\n"
        f"Name: {lead.first_name} {lead.last_name}\n"
        f"Email: {lead.email}\n"
        f"Submitted: {submitted}\n\n"
        f"Review lead:\n{lead_url}"
    )
    message_html = f"""
    <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto;">
      <p>A new lead was submitted.</p>
      <table cellpadding="4" cellspacing="0">
        <tr><td><strong>Name</strong></td><td>{first_name} {last_name}</td></tr>
        <tr><td><strong>Email</strong></td><td>{prospect_email}</td></tr>
        <tr><td><strong>Submitted</strong></td><td>{submitted}</td></tr>
      </table>
      <p><a href="{escaped_url}">Review lead</a></p>
    </div>
    """
    return {
        "from": safe_header(email_from),
        "to": [safe_header(attorney_email)],
        "subject": f"New lead: {subject_name}",
        "text": text,
        "html": message_html,
    }
