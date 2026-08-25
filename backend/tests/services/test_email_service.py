from datetime import datetime, timezone

from app.models.lead import Lead, LeadStatus
from app.services import email_service
from app.services.email_service import EmailService, send_lead_emails_safely


def _lead(**overrides) -> Lead:
    defaults = dict(
        id="lead-1",
        reference_number="INT-2026-0001",
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        status=LeadStatus.PENDING,
        resume_filename="resume.pdf",
        resume_path="/tmp/resume.pdf",
        created_at=datetime(2026, 8, 25, 14, 30, tzinfo=timezone.utc),
        updated_at=datetime(2026, 8, 25, 14, 30, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    return Lead(**defaults)


def _service(**overrides) -> EmailService:
    defaults = dict(
        resend_api_key="",
        email_from="Lead Team <leads@example.com>",
        attorney_email="attorney@example.com",
        frontend_url="http://localhost:3000",
        email_backend="preview",
    )
    defaults.update(overrides)
    return EmailService(**defaults)


def test_prospect_confirmation_has_required_recipient_and_content():
    payload = _service()._prospect_payload(_lead())

    assert payload["from"] == "Lead Team <leads@example.com>"
    assert payload["to"] == ["john@example.com"]
    assert payload["subject"] == "We received your information"
    assert "Hi John" in payload["text"]
    assert "received your information and resume" in payload["text"]
    assert "review your submission" in payload["text"]
    assert "/admin/leads/" not in payload["text"]
    assert "attachments" not in payload


def test_attorney_notification_has_required_recipient_content_and_link():
    payload = _service()._attorney_payload(_lead())

    assert payload["to"] == ["attorney@example.com"]
    assert payload["subject"] == "New lead: John Smith"
    assert "Name: John Smith" in payload["text"]
    assert "Email: john@example.com" in payload["text"]
    assert "August 25, 2026 at 14:30 UTC" in payload["text"]
    assert "http://localhost:3000/admin/leads/lead-1" in payload["text"]
    assert "resume.pdf" not in payload["text"]
    assert "attachments" not in payload


def test_naive_database_timestamp_is_rendered_as_utc():
    lead = _lead(created_at=datetime(2026, 8, 25, 14, 30))

    payload = _service()._attorney_payload(lead)

    assert "August 25, 2026 at 14:30 UTC" in payload["text"]


def test_user_values_are_escaped_in_html():
    lead = _lead(
        first_name="<script>alert(1)</script>",
        last_name='Smith"><img src=x onerror=alert(1)>',
        email='john@example.com"><script>alert(1)</script>',
    )

    prospect = _service()._prospect_payload(lead)
    attorney = _service()._attorney_payload(lead)

    assert "<script>alert(1)</script>" not in prospect["html"]
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in prospect["html"]
    assert "<img" not in attorney["html"]
    assert "&lt;img" in attorney["html"]


def test_control_characters_cannot_be_injected_into_headers():
    lead = _lead(
        first_name="John\r\nBcc: attacker@example.com",
        email="john@example.com\r\nBcc: attacker@example.com",
    )

    prospect = _service()._prospect_payload(lead)
    attorney = _service()._attorney_payload(lead)

    for value in [*prospect["to"], attorney["subject"]]:
        assert "\r" not in value
        assert "\n" not in value


def test_resend_backend_invokes_provider(monkeypatch):
    sent = []
    monkeypatch.setattr(email_service.resend.Emails, "send", sent.append)
    service = _service(email_backend="resend", resend_api_key="re_test_key")

    service.send_prospect_confirmation(_lead())

    assert len(sent) == 1
    assert sent[0]["to"] == ["john@example.com"]
    assert "attachments" not in sent[0]
    assert email_service.resend.api_key == "re_test_key"


def test_missing_resend_key_logs_safe_preview(caplog):
    service = _service(email_backend="resend", resend_api_key="")

    with caplog.at_level("WARNING"):
        service.send_prospect_confirmation(_lead())

    assert "DEV EMAIL - NOT DELIVERED" in caplog.text
    assert "john@example.com" in caplog.text
    assert "We received your information" in caplog.text
    assert "resume.pdf" not in caplog.text


def test_smtp_backend_builds_message_without_attachments(monkeypatch):
    messages = []

    class FakeSmtp:
        def __init__(self, host, port, timeout):
            assert (host, port, timeout) == ("mailpit", 1025, 10)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def send_message(self, message):
            messages.append(message)

    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSmtp)
    service = _service(
        email_backend="smtp",
        smtp_host="mailpit",
        smtp_port=1025,
    )

    service.send_attorney_notification(_lead())

    assert len(messages) == 1
    assert messages[0]["To"] == "attorney@example.com"
    assert messages[0]["Subject"] == "New lead: John Smith"
    assert list(messages[0].iter_attachments()) == []


def test_prospect_failure_does_not_prevent_attorney_attempt(caplog):
    api_key = "re_must_not_appear_in_logs"

    class FailingProspectService:
        def __init__(self):
            self.attorney_calls = 0

        def send_prospect_confirmation(self, lead):
            raise RuntimeError(api_key)

        def send_attorney_notification(self, lead):
            self.attorney_calls += 1

    service = FailingProspectService()
    with caplog.at_level("ERROR"):
        send_lead_emails_safely(service, _lead())

    assert service.attorney_calls == 1
    assert "Failed to send prospect email" in caplog.text
    assert api_key not in caplog.text


def test_missing_attorney_configuration_does_not_raise_from_safe_wrapper(caplog):
    service = _service(attorney_email="")

    with caplog.at_level("ERROR"):
        send_lead_emails_safely(service, _lead())

    assert "Failed to send attorney email" in caplog.text
