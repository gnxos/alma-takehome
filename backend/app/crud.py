from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


def create_lead(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    resume_filename: str,
    resume_path: str,
) -> models.Lead:
    lead = models.Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_filename=resume_filename,
        resume_path=resume_path,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: str) -> models.Lead | None:
    return db.get(models.Lead, lead_id)


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
