import re

import dns.exception
import dns.resolver
from email_validator import EmailNotValidError
from email_validator import validate_email as _validate_email_syntax

from app.config import DNS_LOOKUP_TIMEOUT, EMAIL_MAX_LENGTH

_WHITESPACE_RE = re.compile(r"\s")


def domain_has_mail_exchanger(domain: str) -> bool:
    """DNS lookup seam — tests monkeypatch this to avoid live network calls."""
    resolver = dns.resolver.Resolver()
    resolver.lifetime = DNS_LOOKUP_TIMEOUT
    try:
        answers = resolver.resolve(domain, "MX")
        # RFC 7505 "null MX" (a lone "." target, e.g. example.com) explicitly
        # advertises that the domain accepts no mail — don't fall back to A.
        return any(str(record.exchange).strip(".") for record in answers)
    except dns.resolver.NoAnswer:
        pass  # No MX record; RFC 5321 falls back to the domain's A/AAAA record.
    except dns.exception.DNSException:
        return False

    try:
        resolver.resolve(domain, "A")
        return True
    except dns.exception.DNSException:
        return False


def normalize_email(value: str) -> str:
    trimmed = value.strip()
    if len(trimmed) > EMAIL_MAX_LENGTH:
        raise ValueError(f"email must be at most {EMAIL_MAX_LENGTH} characters")
    if _WHITESPACE_RE.search(trimmed):
        raise ValueError("email must not contain spaces or line breaks")

    try:
        validated = _validate_email_syntax(trimmed, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc

    if not domain_has_mail_exchanger(validated.domain):
        raise ValueError("email domain does not have valid DNS/MX records")

    return validated.normalized
