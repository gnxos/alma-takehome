import pytest

from app.services import email_validation

# Captured before the autouse `mock_dns_lookup` fixture (in conftest.py) replaces
# email_validation.domain_has_mail_exchanger, so this test can exercise the real
# implementation's null-MX handling instead of the mock.
_real_domain_has_mail_exchanger = email_validation.domain_has_mail_exchanger


def test_normalize_email_trims_and_lowercases_domain_only():
    assert (
        email_validation.normalize_email("  Ada.Lovelace@EXAMPLE.COM  ")
        == "Ada.Lovelace@example.com"
    )


def test_normalize_email_rejects_missing_at_sign():
    with pytest.raises(ValueError):
        email_validation.normalize_email("ada.example.com")


def test_normalize_email_rejects_missing_dot_in_domain():
    with pytest.raises(ValueError):
        email_validation.normalize_email("ada@localhost")


def test_normalize_email_rejects_internal_space():
    with pytest.raises(ValueError):
        email_validation.normalize_email("ada lovelace@example.com")


def test_normalize_email_rejects_line_break():
    with pytest.raises(ValueError):
        email_validation.normalize_email("ada@example.com\nBcc: evil@example.com")


def test_normalize_email_rejects_over_max_length():
    with pytest.raises(ValueError):
        email_validation.normalize_email(f"{'a' * 90}@example.com")


def test_normalize_email_allows_exactly_max_length(monkeypatch):
    monkeypatch.setattr(email_validation, "domain_has_mail_exchanger", lambda domain: True)
    local_part_len = email_validation.EMAIL_MAX_LENGTH - len("@example.com")
    email = f"{'a' * local_part_len}@example.com"
    assert len(email) == email_validation.EMAIL_MAX_LENGTH
    assert email_validation.normalize_email(email) == email


def test_normalize_email_rejects_when_domain_has_no_mx_or_a_record(monkeypatch):
    monkeypatch.setattr(email_validation, "domain_has_mail_exchanger", lambda domain: False)
    with pytest.raises(ValueError):
        email_validation.normalize_email("ada@no-mail-domain.example")


def test_normalize_email_accepts_when_domain_has_mx_record(monkeypatch):
    monkeypatch.setattr(email_validation, "domain_has_mail_exchanger", lambda domain: True)
    assert email_validation.normalize_email("ada@example.com") == "ada@example.com"


def test_domain_has_mail_exchanger_treats_null_mx_as_no_mail(monkeypatch):
    class FakeRecord:
        exchange = "."

    class FakeResolver:
        lifetime = 0

        def resolve(self, domain, record_type):
            assert record_type == "MX"
            return [FakeRecord()]

    monkeypatch.setattr(email_validation.dns.resolver, "Resolver", FakeResolver)
    assert _real_domain_has_mail_exchanger("example.com") is False
