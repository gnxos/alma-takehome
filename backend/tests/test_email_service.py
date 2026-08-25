from datetime import datetime, timezone

from app import email_service
from app.models import Lead, LeadStatus


def _lead(**overrides) -> Lead:
    defaults = dict(
        id="lead-1",
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
    monkeypatch.setattr(email_service, "_send", sent.append)
    monkeypatch.setattr(email_service, "RESEND_API_KEY", "test-key")

    email_service.send_lead_notifications(_lead())

    assert len(sent) == 2
    prospect_email, attorney_email = sent
    assert prospect_email["to"] == ["ada@example.com"]
    assert attorney_email["to"] == [email_service.ATTORNEY_EMAIL]


def test_prospect_email_greets_lead_by_first_name():
    payload = email_service._prospect_email_payload(_lead(first_name="Grace"))
    assert "Grace" in payload["subject"]
    assert "Grace" in payload["html"]


def test_attorney_email_mentions_alma_and_lead_details():
    payload = email_service._attorney_email_payload(_lead())
    assert "Alma" in payload["html"]
    assert "Ada Lovelace" in payload["html"]
    assert "ada@example.com" in payload["html"]
    assert payload["to"] == [email_service.ATTORNEY_EMAIL]


def test_email_payloads_escape_html_in_names():
    payload = email_service._prospect_email_payload(
        _lead(first_name="A<script>", last_name="Doe")
    )
    assert "<script>" not in payload["html"]
    assert "&lt;script&gt;" in payload["html"]


def test_send_invokes_resend_when_api_key_present(monkeypatch):
    called_with = []
    monkeypatch.setattr(email_service, "RESEND_API_KEY", "test-api-key")
    monkeypatch.setattr(
        email_service.resend.Emails, "send", lambda payload: called_with.append(payload)
    )

    test_payload = {"from": email_service.EMAIL_FROM, "to": ["ada@example.com"], "subject": "Test"}
    email_service._send(test_payload)

    assert len(called_with) == 1
    assert called_with[0] == test_payload
    assert email_service.resend.api_key == "test-api-key"


def test_email_payloads_include_configured_sender():
    lead = _lead()
    prospect = email_service._prospect_email_payload(lead)
    attorney = email_service._attorney_email_payload(lead)
    assert prospect["from"] == email_service.EMAIL_FROM
    assert attorney["from"] == email_service.EMAIL_FROM


def test_send_skips_without_api_key(monkeypatch, caplog):
    monkeypatch.setattr(email_service, "RESEND_API_KEY", "")
    with caplog.at_level("WARNING"):
        email_service._send({"subject": "test"})
    assert "skipping email" in caplog.text.lower()


def test_send_swallows_resend_errors(monkeypatch, caplog):
    monkeypatch.setattr(email_service, "RESEND_API_KEY", "test-key")

    def _raise(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(email_service.resend.Emails, "send", _raise)
    with caplog.at_level("ERROR"):
        email_service._send({"subject": "test"})  # must not raise
    assert "failed to send email" in caplog.text.lower()


