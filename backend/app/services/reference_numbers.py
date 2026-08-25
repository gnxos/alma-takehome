import random
from datetime import datetime, timezone


def generate_reference_number() -> str:
    """Return a docket-style ticket number such as ``INT-2026-7473``."""
    year = datetime.now(timezone.utc).year
    digits = random.randint(1000, 9999)
    return f"INT-{year}-{digits}"
