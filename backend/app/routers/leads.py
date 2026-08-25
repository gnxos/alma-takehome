import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import config, crud, email_service, resume_validation, schemas
from app.auth import get_current_attorney_email
from app.database import get_db
from app.models import LeadStatus

# Applied to every internal-dashboard route below (list/get/update/resume) —
# lead creation stays public since prospects submit it unauthenticated.
_require_attorney = Depends(get_current_attorney_email)

router = APIRouter(prefix="/api/leads", tags=["leads"])


async def _save_resume(resume: UploadFile) -> tuple[str, str]:
    extension = Path(resume.filename or "").suffix.lower()
    if extension not in config.ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume must be one of: {', '.join(sorted(config.ALLOWED_RESUME_EXTENSIONS))}",
        )

    contents = await resume.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Resume file is empty"
        )
    if len(contents) < config.MIN_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume must be at least {config.MIN_RESUME_SIZE_BYTES} bytes",
        )
    if len(contents) > config.MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume must be smaller than {config.MAX_RESUME_SIZE_BYTES // (1024 * 1024)}MB",
        )

    try:
        resume_validation.validate_resume_contents(extension, contents)
    except resume_validation.ResumeValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    stored_name = f"{uuid.uuid4()}{extension}"
    stored_path = config.UPLOAD_DIR / stored_name
    stored_path.write_bytes(contents)
    return resume.filename or stored_name, str(stored_path)


@router.post("", response_model=schemas.LeadOut, status_code=status.HTTP_201_CREATED)
async def create_lead(
    request: Request,
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Public endpoint: prospects submit this form to become a lead."""
    form = await request.form()
    if len(form.getlist("resume")) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only one resume file may be uploaded.",
        )

    try:
        validated = schemas.LeadBase(first_name=first_name, last_name=last_name, email=email)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422, detail=exc.errors(include_context=False, include_url=False)
        )

    original_filename, stored_path = await _save_resume(resume)
    lead = crud.create_lead(
        db,
        first_name=validated.first_name,
        last_name=validated.last_name,
        email=validated.email,
        resume_filename=original_filename,
        resume_path=stored_path,
    )
    # Runs after the response is sent, so a slow/failing email provider never
    # delays lead creation for the prospect.
    background_tasks.add_task(email_service.send_lead_notifications, lead)
    return lead


@router.get("", response_model=schemas.LeadList)
def list_leads(
    status_filter: LeadStatus | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _attorney_email: str = _require_attorney,
):
    total, items = crud.list_leads(db, status=status_filter, skip=skip, limit=limit)
    return schemas.LeadList(total=total, items=items)


@router.get("/{lead_id}", response_model=schemas.LeadOut)
def get_lead(lead_id: str, db: Session = Depends(get_db), _attorney_email: str = _require_attorney):
    lead = crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=schemas.LeadOut)
def update_lead(
    lead_id: str,
    changes: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    _attorney_email: str = _require_attorney,
):
    lead = crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return crud.update_lead(db, lead, changes)


@router.get("/{lead_id}/resume")
def download_resume(
    lead_id: str, db: Session = Depends(get_db), _attorney_email: str = _require_attorney
):
    lead = crud.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    path = Path(lead.resume_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found")
    return FileResponse(path, filename=lead.resume_filename)
