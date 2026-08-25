from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.reference import generate_reference_number

_MAX_REFERENCE_ATTEMPTS = 5


def create_lead(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    resume_filename: str,
    resume_path: str,
) -> models.Lead:
    for _ in range(_MAX_REFERENCE_ATTEMPTS):
        lead = models.Lead(
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
            # Reference number collision (extremely unlikely) — retry with a new one.
            db.rollback()
            continue
        db.refresh(lead)
        return lead
    raise RuntimeError("Could not generate a unique reference number")


def get_lead(db: Session, lead_id: str) -> models.Lead | None:
    return db.get(models.Lead, lead_id)


def get_lead_by_reference(db: Session, reference_number: str) -> models.Lead | None:
    return (
        db.query(models.Lead)
        .filter(models.Lead.reference_number == reference_number)
        .first()
    )


def get_lead_by_id_or_reference(db: Session, lead_id: str) -> models.Lead | None:
    return get_lead(db, lead_id) or get_lead_by_reference(db, lead_id)


def get_lead_by_email(db: Session, email: str) -> models.Lead | None:
    """Existing ticket for this prospect, if any — used to prevent duplicate
    submissions from re-creating a new lead for the same person."""
    return (
        db.query(models.Lead)
        .filter(models.Lead.email == email)
        .order_by(models.Lead.created_at.desc())
        .first()
    )


def list_leads(
    db: Session,
    *,
    status: models.LeadStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[int, list[models.Lead]]:
    query = db.query(models.Lead)
    if status is not None:
        query = query.filter(models.Lead.status == status)
    total = query.with_entities(func.count(models.Lead.id)).scalar() or 0
    items = (
        query.order_by(models.Lead.created_at.desc()).offset(skip).limit(limit).all()
    )
    return total, items


def update_lead(
    db: Session, lead: models.Lead, changes: schemas.LeadUpdate
) -> models.Lead:
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead
