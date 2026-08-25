import html

from app.models.lead import Lead
from ._shared import EmailPayload, safe_header

SUBJECT = "We received your information"


def build_prospect_email(lead: Lead, *, email_from: str) -> EmailPayload:
    first_name = html.escape(lead.first_name, quote=True)
    ref_number = html.escape(lead.reference_number, quote=True) if getattr(lead, "reference_number", None) else ""
    ref_section_html = (
        f"""
      <div style="background-color: #f3f4f6; border-radius: 6px; padding: 12px 16px; margin: 16px 0; border: 1px solid #e5e7eb;">
        <p style="margin: 0; font-size: 13px; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Your Ticket Reference</p>
        <p style="margin: 4px 0 0 0; font-size: 18px; font-weight: bold; color: #111827; letter-spacing: 1px;">{ref_number}</p>
      </div>
        """
        if ref_number
        else ""
    )
    ref_section_text = f"\nYour Ticket Reference: {ref_number}\n" if ref_number else ""
    text = (
        f"Hi {lead.first_name},\n\n"
        "Thank you for contacting us. We received your information and resume.\n"
        f"{ref_section_text}"
        "Our team will review your submission and contact you if needed."
    )
    message_html = f"""
    <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto; color: #1f2937; line-height: 1.5;">
      <p>Hi {first_name},</p>
      <p>Thank you for contacting us. We received your information and resume.</p>
      {ref_section_html}
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
