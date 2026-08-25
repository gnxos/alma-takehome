from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.lead import Lead, LeadStatus
from app.schemas.leads import LeadUpdate


def create(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    resume_filename: str,
    resume_path: str,
) -> Lead:
    lead = Lead(
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


def get(db: Session, lead_id: str) -> Lead | None:
    return db.get(Lead, lead_id)


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
