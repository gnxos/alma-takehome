import pytest

from app.resume_validation import ResumeValidationError, validate_resume_contents
from tests.factories import GARBAGE_BYTES, make_docx_bytes, make_pdf_bytes


def test_validate_resume_contents_accepts_valid_pdf():
    validate_resume_contents(".pdf", make_pdf_bytes())


def test_validate_resume_contents_rejects_corrupted_pdf():
    with pytest.raises(ResumeValidationError, match="corrupted"):
        validate_resume_contents(".pdf", GARBAGE_BYTES)


def test_validate_resume_contents_rejects_password_protected_pdf():
    with pytest.raises(ResumeValidationError, match="password"):
        validate_resume_contents(".pdf", make_pdf_bytes(password="secret"))


def test_validate_resume_contents_accepts_valid_docx():
    validate_resume_contents(".docx", make_docx_bytes())


def test_validate_resume_contents_rejects_corrupted_docx():
    with pytest.raises(ResumeValidationError, match="corrupted"):
        validate_resume_contents(".docx", GARBAGE_BYTES)


def test_validate_resume_contents_rejects_password_protected_docx(monkeypatch):
    from app import resume_validation

    monkeypatch.setattr(resume_validation, "is_office_file_encrypted", lambda f: True)
    with pytest.raises(ResumeValidationError, match="password"):
        validate_resume_contents(".docx", make_docx_bytes())


def test_validate_resume_contents_rejects_corrupted_doc():
    with pytest.raises(ResumeValidationError, match="corrupted"):
        validate_resume_contents(".doc", GARBAGE_BYTES)


def test_validate_resume_contents_rejects_password_protected_doc(monkeypatch):
    from app import resume_validation

    monkeypatch.setattr(resume_validation, "is_office_file_encrypted", lambda f: True)
    # We can't easily craft a real legacy .doc file without MS Word; the
    # encryption check itself is what's under test here.
    with pytest.raises(ResumeValidationError, match="password"):
        validate_resume_contents(".doc", GARBAGE_BYTES)
