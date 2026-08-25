import re
from datetime import datetime, timezone
from typing import Any

EmailPayload = dict[str, Any]

_HEADER_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]+")


def safe_header(value: str) -> str:
    return " ".join(_HEADER_CONTROL_CHARACTERS.sub(" ", value).split())


def format_submission_time(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    rendered = value.strftime("%B %d, %Y at %H:%M %Z").strip()
    return rendered.replace(" 0", " ")
