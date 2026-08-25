import re

from app.services.reference_numbers import (
    CROCKFORD_BASE32_ALPHABET,
    generate_reference_number,
)

REFERENCE_NUMBER_RE = re.compile(r"^INT-\d{4}-[0-9A-HJ-NP-Z]{6}$")


def test_generate_reference_number_format():
    ref = generate_reference_number()
    assert REFERENCE_NUMBER_RE.match(ref)


def test_generate_reference_number_excludes_ambiguous_characters():
    # Crockford's Base32 excludes I, L, O, and U
    ambiguous = {"I", "L", "O", "U"}
    for _ in range(100):
        ref = generate_reference_number()
        suffix = ref.split("-")[2]
        assert not any(char in ambiguous for char in suffix)
        assert all(char in CROCKFORD_BASE32_ALPHABET for char in suffix)


def test_generate_reference_number_is_unique():
    # Across 1000 generations, collision probability with 1.07B keys is ~0.04%
    numbers = [generate_reference_number() for _ in range(1000)]
    assert len(set(numbers)) == 1000


def test_generate_reference_number_custom_length():
    ref = generate_reference_number(length=8)
    assert re.match(r"^INT-\d{4}-[0-9A-HJ-NP-Z]{8}$", ref)
