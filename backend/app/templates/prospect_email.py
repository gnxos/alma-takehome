import html

from app.models.lead import Lead
from app.templates._shared import EmailPayload, safe_header

SUBJECT = "We received your information"


def build_prospect_email(lead: Lead, *, email_from: str) -> EmailPayload:
    first_name = html.escape(lead.first_name, quote=True)
    text = (
        f"Hi {lead.first_name},\n\n"
        "Thank you for contacting us. We received your information and resume.\n"
        "Our team will review your submission and contact you if needed."
    )
    message_html = f"""
    <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto;">
      <p>Hi {first_name},</p>
      <p>Thank you for contacting us. We received your information and resume.</p>
      <p>Our team will review your submission and contact you if needed.</p>
    </div>
    """
    return {
        "from": safe_header(email_from),
        "to": [safe_header(lead.email)],
        "subject": SUBJECT,
        "text": text,
        "html": message_html,
    }
