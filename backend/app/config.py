import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'leads.db'}")
if DATABASE_URL.startswith("sqlite:///"):
    _sqlite_file = Path(DATABASE_URL[len("sqlite:///") :])
    if _sqlite_file.parent:
        _sqlite_file.parent.mkdir(parents=True, exist_ok=True)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
MIN_RESUME_SIZE_BYTES = 100  # anything smaller can't be a real pdf/doc/docx
MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 36

EMAIL_MAX_LENGTH = 100

# Seconds to wait for an MX/A DNS lookup before treating a domain as undeliverable.
DNS_LOOKUP_TIMEOUT = 3

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Empty by default: local dev/tests never send real email unless a real key is set.
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
# resend.dev's sandbox sender works without a verified domain, for local testing.
EMAIL_FROM = os.getenv("EMAIL_FROM", "Alma <onboarding@resend.dev>")
ATTORNEY_EMAIL = os.getenv("ATTORNEY_EMAIL", "attorney@alma.example.com")

# The single hardcoded attorney account for the internal dashboard.
# Override all three via env vars for anything beyond local dev.
ATTORNEY_PASSWORD = os.getenv("ATTORNEY_PASSWORD", "Alma123!")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-insecure-secret-change-me")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", str(60 * 24)))  # 24h

AUTH_COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
# "lax" is sufficient for same-site deployments (including localhost across
# ports); a cross-domain frontend/backend split in production would need
# "none" here plus COOKIE_SECURE=true.
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
