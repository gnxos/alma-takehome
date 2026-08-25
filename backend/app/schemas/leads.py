import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from app.core.config import NAME_MAX_LENGTH, NAME_MIN_LENGTH
from app.models.lead import EmailDeliveryStatus, LeadStatus
from app.services.email_validation import normalize_email

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_name(value: str, *, field_name: str) -> str:
    value = _WHITESPACE_RE.sub(" ", value.strip())
    if not (NAME_MIN_LENGTH <= len(value) <= NAME_MAX_LENGTH):
        raise ValueError(
            f"{field_name} must be between {NAME_MIN_LENGTH} and "
            f"{NAME_MAX_LENGTH} characters"
        )
    if not all(character.isalpha() or character == " " for character in value):
        raise ValueError(f"{field_name} may only contain letters and spaces")
    return value


class _NameValidationMixin:
    @field_validator("first_name", "last_name", mode="after")
    @classmethod
    def _validate_name(
        cls,
        value: Optional[str],
        info: ValidationInfo,
    ) -> Optional[str]:
        if value is None:
            return value
        return normalize_name(value, field_name=info.field_name)


class _EmailValidationMixin:
    @field_validator("email", mode="after")
    @classmethod
    def _validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return normalize_email(value)


class LeadFields(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None


class LeadBase(_NameValidationMixin, _EmailValidationMixin, LeadFields):
    pass


class LeadUpdate(_NameValidationMixin, _EmailValidationMixin, BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[LeadStatus] = None
    phone: Optional[str] = None
    message: Optional[str] = None


class LeadOut(LeadFields):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reference_number: str
    status: LeadStatus
    resume_filename: str
    prospect_email_status: EmailDeliveryStatus
    attorney_email_status: EmailDeliveryStatus
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class LeadList(BaseModel):
    total: int
    items: list[LeadOut]


class LeadCreateResult(LeadOut):
    """Creation response that identifies an existing duplicate submission."""

    already_exists: bool = False
