import re

from app.services.reference_numbers import generate_reference_number

REFERENCE_NUMBER_RE = re.compile(r"^INT-\d{4}-\d{4}$")


def test_generate_reference_number_format():
    assert REFERENCE_NUMBER_RE.match(generate_reference_number())


def test_generate_reference_number_is_not_constant():
    numbers = {generate_reference_number() for _ in range(20)}
    assert len(numbers) > 1
