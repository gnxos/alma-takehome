from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.lead import Lead, LeadStatus
from app.schemas.leads import LeadUpdate
from app.services.reference_numbers import generate_reference_number

_MAX_REFERENCE_ATTEMPTS = 5


def create(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    resume_filename: str,
    resume_path: str,
) -> Lead:
    for _ in range(_MAX_REFERENCE_ATTEMPTS):
        lead = Lead(
            reference_number=generate_reference_number(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            resume_filename=resume_filename,
            resume_path=resume_path,
        )
        db.add(lead)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(lead)
        return lead
    raise RuntimeError("Could not generate a unique reference number")


def get(db: Session, lead_id: str) -> Lead | None:
    return db.get(Lead, lead_id)


def get_by_reference(db: Session, reference_number: str) -> Lead | None:
    return (
        db.query(Lead)
        .filter(Lead.reference_number == reference_number)
        .first()
    )


def get_by_id_or_reference(db: Session, identifier: str) -> Lead | None:
    return get(db, identifier) or get_by_reference(db, identifier)


def get_by_email(db: Session, email: str) -> Lead | None:
    return (
        db.query(Lead)
        .filter(Lead.email == email)
        .order_by(Lead.created_at.desc())
        .first()
    )


def list_by_email(db: Session, email: str) -> list[Lead]:
    normalized_email = email.strip().lower()
    return (
        db.query(Lead)
        .filter(func.lower(Lead.email) == normalized_email)
        .order_by(Lead.created_at.desc())
        .all()
    )


def list_all(
    db: Session,
    *,
    status: LeadStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[int, list[Lead]]:
    query = db.query(Lead)
    if status is not None:
        query = query.filter(Lead.status == status)
    total = query.with_entities(func.count(Lead.id)).scalar() or 0
    items = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    return total, items


def update(db: Session, lead: Lead, changes: LeadUpdate) -> Lead:
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead
