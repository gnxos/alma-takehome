import secrets
from datetime import datetime, timezone

# Crockford's Base32 character set:
# Excludes I, L, O, and U to avoid visual ambiguity (e.g. 1 vs I/l, 0 vs O)
# and to prevent accidental offensive substrings.
CROCKFORD_BASE32_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
DEFAULT_SUFFIX_LENGTH = 6


def generate_reference_number(length: int = DEFAULT_SUFFIX_LENGTH) -> str:
    """Return a collision-resistant, human-readable ticket reference number.

    Format: ``INT-<YYYY>-<SUFFIX>`` (e.g., ``INT-2026-8K7M4P``).
    Uses cryptographically secure random selection (CSPRNG via ``secrets``)
    from Crockford's Base32 character set (32^6 = 1,073,741,824 combinations/year).
    """
    year = datetime.now(timezone.utc).year
    suffix = "".join(secrets.choice(CROCKFORD_BASE32_ALPHABET) for _ in range(length))
    return f"INT-{year}-{suffix}"
