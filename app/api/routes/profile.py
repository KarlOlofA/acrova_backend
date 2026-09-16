from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.enums import CVStatus
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
        cv_analysis.parse_cv(candidate.cv_storage_path)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.get("/{profile_id}", response_model=CandidateProfileRead)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    profile = db.get(CandidateProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
