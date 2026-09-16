from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.base import utcnow
from app.models.candidate import Candidate
from app.models.enums import CVStatus, ProfileSourceType, ProfileStatus
from app.models.profile import CandidateProfile
from app.schemas.profile import CandidateProfileRead, CVAnalyzeRequest
from app.services import cv_analysis

router = APIRouter(prefix="/profile", tags=["profiles"])


@router.post("/cv/analyze", response_model=CandidateProfileRead)
async def analyze_cv(payload: CVAnalyzeRequest, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, payload.candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.cv_status != CVStatus.UPLOADED or not candidate.cv_storage_path:
        raise HTTPException(status_code=400, detail="Candidate has no uploaded CV to analyze")

    try:
        claims = cv_analysis.parse_cv(candidate.cv_storage_path)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    profile = CandidateProfile(
        candidate_id=candidate.id,
        source_type=ProfileSourceType.CV,
        status=ProfileStatus.COMPLETED,
        extracted_claims=claims,
        analyzed_at=utcnow(),
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=CandidateProfileRead)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.get(CandidateProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
