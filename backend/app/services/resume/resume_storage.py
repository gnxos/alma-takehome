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


# TODO (Production - AWS S3 / Cloudflare R2 Object Storage):
# For production storage of uploaded resumes:
# 1. Initialize boto3 S3 client with IAM role / AWS credentials.
# 2. Upload file stream to private S3 bucket:
#    s3_client.upload_fileobj(resume.file, BUCKET_NAME, f"resumes/{stored_name}")
# 3. Generate short-lived presigned GET URLs for authorized attorney downloads:
#    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': key}, ExpiresIn=300)
# 4. Configure S3 bucket lifecycle rules for automated retention / archival.
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


def delete_stored_resume(stored_resume: StoredResume) -> None:
    stored_resume.path.unlink(missing_ok=True)
