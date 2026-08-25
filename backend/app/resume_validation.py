import io

import docx
import msoffcrypto
from pypdf import PdfReader


class ResumeValidationError(ValueError):
    """Raised when a resume file cannot be safely accepted."""


def is_office_file_encrypted(file_obj: io.BytesIO) -> bool:
    """Encryption-check seam — tests monkeypatch this to avoid crafting real files."""
    file_obj.seek(0)
    return msoffcrypto.OfficeFile(file_obj).is_encrypted()


def _validate_pdf(contents: bytes) -> None:
    try:
        reader = PdfReader(io.BytesIO(contents))
        if reader.is_encrypted:
            raise ResumeValidationError("The PDF file is password protected.")
        if len(reader.pages) == 0:
            raise ResumeValidationError("The PDF file has no readable pages.")
    except ResumeValidationError:
        raise
    except Exception as exc:
        raise ResumeValidationError("The PDF file is corrupted or unreadable.") from exc


def _validate_office_file(contents: bytes, *, kind: str) -> None:
    try:
        encrypted = is_office_file_encrypted(io.BytesIO(contents))
    except Exception as exc:
        raise ResumeValidationError(f"The {kind} file is corrupted or unreadable.") from exc
    if encrypted:
        raise ResumeValidationError(f"The {kind} file is password protected.")

    if kind == "DOCX":
        try:
            document = docx.Document(io.BytesIO(contents))
            _ = document.paragraphs  # forces document.xml to actually be parsed
        except Exception as exc:
            raise ResumeValidationError("The DOCX file is corrupted or unreadable.") from exc


_VALIDATORS = {
    ".pdf": lambda contents: _validate_pdf(contents),
    ".docx": lambda contents: _validate_office_file(contents, kind="DOCX"),
    ".doc": lambda contents: _validate_office_file(contents, kind="DOC"),
}


def validate_resume_contents(extension: str, contents: bytes) -> None:
    validator = _VALIDATORS.get(extension)
    if validator is None:
        raise ResumeValidationError(f"Unsupported resume type: {extension}")
    validator(contents)
