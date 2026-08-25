import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'leads.db'}")
if DATABASE_URL.startswith("sqlite:///"):
    _sqlite_file = Path(DATABASE_URL[len("sqlite:///") :])
    if _sqlite_file.parent:
        _sqlite_file.parent.mkdir(parents=True, exist_ok=True)

# TODO (Production - AWS S3 Storage):
# Set AWS_S3_BUCKET, AWS_REGION, and AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY (or use IAM role)
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
MIN_RESUME_SIZE_BYTES = 100
MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 36
EMAIL_MAX_LENGTH = 100
DNS_LOOKUP_TIMEOUT = 3

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Lead-notification emails: EmailService supports three backends.
# - "smtp" (default here): local dev — points at a local Mailpit instance
#   (https://mailpit.axllent.org) by default; run `docker compose up mailpit`
#   and view caught mail at http://localhost:8025.
# - "resend": production — set EMAIL_BACKEND=resend and RESEND_API_KEY to
#   send via Resend's HTTP API instead.
# - "preview": logs the email instead of sending (used when a backend is
#   selected but not fully configured, e.g. resend with no API key).
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "Alma <onboarding@alma.example.com>")
ATTORNEY_EMAIL = os.getenv("ATTORNEY_EMAIL", "attorney@alma.example.com")
ATTORNEY_EMAILS = os.getenv(
    "ATTORNEY_EMAILS",
    "attorney@alma.example.com,sarah.jenkins@alma.example.com,michael.chang@alma.example.com",
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "smtp")
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_TIMEOUT_SECONDS = float(os.getenv("SMTP_TIMEOUT_SECONDS", "10"))

ATTORNEY_PASSWORD = os.getenv("ATTORNEY_PASSWORD", "Alma123!")

# Configured attorney accounts (email -> {name, password})
DEFAULT_ATTORNEYS: dict[str, dict[str, str]] = {
    "attorney@alma.example.com": {
        "name": "Managing Attorney",
        "password": os.getenv("ATTORNEY_PASSWORD", "Alma123!"),
    },
    "sarah.jenkins@alma.example.com": {
        "name": "Sarah Jenkins, Esq.",
        "password": os.getenv("ATTORNEY_PASSWORD_SARAH", "Alma123!"),
    },
    "michael.chang@alma.example.com": {
        "name": "Michael Chang, Esq.",
        "password": os.getenv("ATTORNEY_PASSWORD_MICHAEL", "Alma123!"),
    },
}

JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-insecure-secret-change-me")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", str(60 * 24)))

AUTH_COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
