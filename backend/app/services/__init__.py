"""Business and infrastructure services."""

import sys
from app.services.email import email_notifications, email_validation
from app.services.resume import resume_storage, resume_validation

# Backward compatibility for direct module imports
sys.modules["app.services.email_notifications"] = email_notifications
sys.modules["app.services.email_validation"] = email_validation
sys.modules["app.services.resume_storage"] = resume_storage
sys.modules["app.services.resume_validation"] = resume_validation

__all__ = [
    "email_notifications",
    "email_validation",
    "resume_storage",
    "resume_validation",
]
