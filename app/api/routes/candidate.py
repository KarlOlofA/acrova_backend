import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.base import utcnow
from app.models.candidate import Candidate
from app.models.enums import CVStatus
from app.models.user import User
from app.schemas.candidate import (
    CandidateCreate,
    CandidateRead,
    CVConfirmResponse,
    CVUploadURLResponse,
)
from app.services import supabase_storage

router = APIRouter(prefix="/candidate", tags=["candidates"])


def _get_owned_candidate(candidate_id: str, current_user: User, db: Session) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this candidate")
    return candidate


@router.post("/create", response_model=CandidateRead, status_code=201)
async def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    candidate = Candidate(user_id=payload.user_id)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.get("/{candidate_id}/profiles")
async def list_candidate_profiles(candidate_id: str):
    return {"profiles": []}


@router.post("/{candidate_id}/cv/upload-url", response_model=CVUploadURLResponse)
async def create_cv_upload_url(
    candidate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = _get_owned_candidate(candidate_id, current_user, db)
    storage_path = f"{candidate.id}/{uuid.uuid4()}.pdf"
    try:
        result = await supabase_storage.create_signed_upload_url(storage_path)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    candidate.cv_storage_path = result["path"]
    candidate.cv_status = CVStatus.PENDING
    db.commit()

    return CVUploadURLResponse(
        upload_url=result["upload_url"], token=result.get("token"), storage_path=result["path"]
    )


@router.post("/{candidate_id}/cv/confirm", response_model=CVConfirmResponse)
async def confirm_cv_upload(
    candidate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = _get_owned_candidate(candidate_id, current_user, db)
    if candidate.cv_status != CVStatus.PENDING or not candidate.cv_storage_path:
        raise HTTPException(status_code=400, detail="No pending CV upload for this candidate")
    candidate.cv_status = CVStatus.UPLOADED
    candidate.cv_uploaded_at = utcnow()
    db.commit()
    db.refresh(candidate)
    return candidate
