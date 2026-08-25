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

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "Alma <onboarding@resend.dev>")
ATTORNEY_EMAIL = os.getenv("ATTORNEY_EMAIL", "attorney@alma.example.com")

ATTORNEY_PASSWORD = os.getenv("ATTORNEY_PASSWORD", "Alma123!")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-insecure-secret-change-me")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", str(60 * 24)))

AUTH_COOKIE_NAME = "access_token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
