import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import UploadFile

from app.core import config
from app.services.resume.resume_validation import ResumeValidationError, validate_resume_contents


class ResumeStorageError(ValueError):
    """Raised when an uploaded resume cannot be safely stored."""


@dataclass(frozen=True)
class StoredResume:
    original_filename: str
    path: Path


async def store_resume(resume: UploadFile) -> StoredResume:
    extension = Path(resume.filename or "").suffix.lower()
    if extension not in config.ALLOWED_RESUME_EXTENSIONS:
        allowed = ", ".join(sorted(config.ALLOWED_RESUME_EXTENSIONS))
        raise ResumeStorageError(f"Resume must be one of: {allowed}")

    contents = await resume.read()
    if not contents:
        raise ResumeStorageError("Resume file is empty")
    if len(contents) < config.MIN_RESUME_SIZE_BYTES:
        raise ResumeStorageError(
            f"Resume must be at least {config.MIN_RESUME_SIZE_BYTES} bytes"
        )
    if len(contents) > config.MAX_RESUME_SIZE_BYTES:
        max_megabytes = config.MAX_RESUME_SIZE_BYTES // (1024 * 1024)
        raise ResumeStorageError(f"Resume must be smaller than {max_megabytes}MB")

    try:
        validate_resume_contents(extension, contents)
    except ResumeValidationError as exc:
        raise ResumeStorageError(str(exc)) from exc

    stored_name = f"{uuid.uuid4()}{extension}"
    stored_path = config.UPLOAD_DIR / stored_name
    stored_path.write_bytes(contents)
    return StoredResume(
        original_filename=resume.filename or stored_name,
        path=stored_path,
    )
