import random
from datetime import datetime, timezone


def generate_reference_number() -> str:
    """A docket-style ticket number, e.g. INT-2026-7473."""
    year = datetime.now(timezone.utc).year
    digits = random.randint(1000, 9999)
    return f"INT-{year}-{digits}"
