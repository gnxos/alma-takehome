import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped

from app.database.base import Base


class LeadStatus(str, enum.Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


class EmailDeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


def _uuid() -> str:
    return str(uuid.uuid4())


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = Column(String(36), primary_key=True, default=_uuid)
    reference_number = Column(String(32), nullable=False, unique=True, index=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    resume_filename = Column(String(255), nullable=False)
    resume_path = Column(String(1024), nullable=False)
    status = Column(Enum(LeadStatus), nullable=False, default=LeadStatus.PENDING)
    phone = Column(String(32), nullable=True)
    message = Column(Text, nullable=True)
    prospect_email_status = Column(
        Enum(EmailDeliveryStatus), nullable=False, default=EmailDeliveryStatus.PENDING
    )
    attorney_email_status = Column(
        Enum(EmailDeliveryStatus), nullable=False, default=EmailDeliveryStatus.PENDING
    )
    resolved_by = Column(String(255), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
