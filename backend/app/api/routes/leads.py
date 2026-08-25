from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import get_current_attorney_email
from app.database.session import get_db
from app.models.lead import EmailDeliveryStatus, Lead, LeadStatus
from app.repositories import leads as lead_repository
from app.schemas.leads import (
    LeadBase,
    LeadCreateResult,
    LeadList,
    LeadOut,
    LeadUpdate,
)
from app.services import email_notifications
from app.services.resume_storage import ResumeStorageError, store_resume

router = APIRouter(prefix="/api/leads", tags=["leads"])

# Lead creation is public. Every dashboard endpoint requires this dependency.
_require_attorney = Depends(get_current_attorney_email)


@router.post(
    "",
    response_model=LeadCreateResult,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    phone: str | None = Form(None),
    message: str | None = Form(None),
    db: Session = Depends(get_db),
) -> LeadCreateResult:
    form = await request.form()
    if len(form.getlist("resume")) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one resume file may be uploaded.",
        )

    try:
        validated = LeadBase(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            message=message,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_context=False, include_url=False),
        ) from exc

    existing = lead_repository.get_pending_by_email(db, validated.email)
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        result = LeadCreateResult.model_validate(existing)
        result.already_exists = True
        return result

    try:
        stored_resume = await store_resume(resume)
    except ResumeStorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    lead = lead_repository.create(
        db,
        first_name=validated.first_name,
        last_name=validated.last_name,
        email=validated.email,
        resume_filename=stored_resume.original_filename,
        resume_path=str(stored_resume.path),
        phone=validated.phone,
        message=validated.message,
    )
    background_tasks.add_task(
        _send_lead_notifications_and_record_status, db.get_bind(), lead.id
    )
    return LeadCreateResult.model_validate(lead)


@router.get("", response_model=LeadList)
def list_leads(
    status_filter: LeadStatus | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _attorney_email: str = _require_attorney,
) -> LeadList:
    total, items = lead_repository.list_all(
        db,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return LeadList(total=total, items=items)


@router.get("/by-email", response_model=LeadList)
def list_leads_by_email(
    email: str,
    db: Session = Depends(get_db),
    _attorney_email: str = _require_attorney,
) -> LeadList:
    items = lead_repository.list_by_email(db, email)
    return LeadList(total=len(items), items=items)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    _attorney_email: str = _require_attorney,
) -> Lead:
    return _get_lead_or_404(db, lead_id)


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: str,
    changes: LeadUpdate,
    db: Session = Depends(get_db),
    _attorney_email: str = _require_attorney,
) -> Lead:
    lead = _get_lead_or_404(db, lead_id)
    return lead_repository.update(db, lead, changes)


@router.get("/{lead_id}/resume")
def download_resume(
    lead_id: str,
    db: Session = Depends(get_db),
    _attorney_email: str = _require_attorney,
) -> FileResponse:
    lead = _get_lead_or_404(db, lead_id)
    path = Path(lead.resume_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found")
    return FileResponse(path, filename=lead.resume_filename)


def _get_lead_or_404(db: Session, lead_id: str) -> Lead:
    lead = lead_repository.get_by_id_or_reference(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


def _send_lead_notifications_and_record_status(engine: Engine, lead_id: str) -> None:
    """Runs as a background task, after the response has already been sent —
    the request's `db` session is closed by then, so this opens its own,
    bound to the same engine the request used (not a hardcoded global one,
    so this stays correct under the test suite's overridden test database)."""
    db = sessionmaker(bind=engine)()
    try:
        lead = lead_repository.get(db, lead_id)
        if lead is None:
            return
        prospect_sent = email_notifications.send_prospect_email(lead)
        attorney_sent = email_notifications.send_attorney_email(lead)
        lead_repository.update_email_statuses(
            db,
            lead,
            prospect_status=(
                EmailDeliveryStatus.SENT if prospect_sent else EmailDeliveryStatus.FAILED
            ),
            attorney_status=(
                EmailDeliveryStatus.SENT if attorney_sent else EmailDeliveryStatus.FAILED
            ),
        )
    finally:
        db.close()
