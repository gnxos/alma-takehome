from datetime import datetime, timezone

from app.models.lead import Lead, LeadStatus
from app.services import email_notifications


def _lead(**overrides) -> Lead:
    defaults = dict(
        id="lead-1",
        reference_number="INT-2026-000001",
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        status=LeadStatus.PENDING,
        resume_filename="resume.pdf",
        resume_path="/tmp/resume.pdf",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    return Lead(**defaults)


def test_send_lead_notifications_emails_prospect_and_attorney(monkeypatch):
    sent = []
    monkeypatch.setattr(email_notifications, "_send", sent.append)

    email_notifications.send_lead_notifications(_lead())

    assert len(sent) == 2
    prospect_email, attorney_email = sent
    assert prospect_email["to"] == ["ada@example.com"]
    assert attorney_email["to"] == [email_notifications.ATTORNEY_EMAIL]


def test_prospect_email_greets_lead_by_first_name():
    payload = email_notifications._prospect_email_payload(_lead(first_name="Grace"))
    assert "Grace" in payload["subject"]
    assert "Grace" in payload["html"]


def test_prospect_email_includes_reference_number():
    payload = email_notifications._prospect_email_payload(
        _lead(reference_number="INT-2026-ABC123")
    )
    assert "INT-2026-ABC123" in payload["html"]
    assert "Your Ticket Reference" in payload["html"]


def test_attorney_email_mentions_alma_and_lead_details():
    payload = email_notifications._attorney_email_payload(_lead())
    assert "Alma" in payload["html"]
    assert "Ada Lovelace" in payload["html"]
    assert "ada@example.com" in payload["html"]
    assert payload["to"] == [email_notifications.ATTORNEY_EMAIL]


def test_email_payloads_escape_html_in_names():
    payload = email_notifications._prospect_email_payload(
        _lead(first_name="A<script>", last_name="Doe")
    )
    assert "<script>" not in payload["html"]
    assert "&lt;script&gt;" in payload["html"]


def test_email_payloads_include_configured_sender():
    lead = _lead()
    prospect = email_notifications._prospect_email_payload(lead)
    attorney = email_notifications._attorney_email_payload(lead)
    assert prospect["from"] == email_notifications.EMAIL_FROM
    assert attorney["from"] == email_notifications.EMAIL_FROM


def test_build_message_sets_headers_and_html_body():
    payload = {
        "from": "Alma <onboarding@alma.example.com>",
        "to": ["ada@example.com", "attorney@alma.example.com"],
        "subject": "Test subject",
        "html": "<p>Hello</p>",
    }
    message = email_notifications._build_message(payload)

    assert message["From"] == payload["from"]
    assert message["To"] == "ada@example.com, attorney@alma.example.com"
    assert message["Subject"] == "Test subject"
    assert "<p>Hello</p>" in message.get_payload()[0].get_payload()


def test_send_delivers_built_message_to_recipients(monkeypatch):
    delivered = []
    monkeypatch.setattr(
        email_notifications,
        "_deliver",
        lambda message, recipients: delivered.append((message, recipients)),
    )

    payload = {
        "from": email_notifications.EMAIL_FROM,
        "to": ["ada@example.com"],
        "subject": "Test",
        "html": "<p>hi</p>",
    }
    email_notifications._send(payload)

    assert len(delivered) == 1
    message, recipients = delivered[0]
    assert recipients == ["ada@example.com"]
    assert message["Subject"] == "Test"


def test_send_swallows_smtp_errors(monkeypatch, caplog):
    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(email_notifications, "_deliver", _raise)
    with caplog.at_level("ERROR"):
        email_notifications._send({"subject": "test", "to": ["a@example.com"], "html": "x"})
    assert "failed to send email" in caplog.text.lower()
