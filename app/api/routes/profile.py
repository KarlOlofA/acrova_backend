from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.profile import CandidateProfileRead, CVUploadResponse
from app.services import cv_analysis

router = APIRouter(prefix="/profile", tags=["profiles"])


@router.post("/cv/upload", response_model=CVUploadResponse)
async def upload_cv(candidate_id: str, file: UploadFile = File(...)):
    try:
        cv_analysis.parse_cv(await file.read())
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.get("/{profile_id}", response_model=CandidateProfileRead)
async def get_profile(profile_id: str):
    raise HTTPException(status_code=501, detail="Fetching a profile analysis is not yet implemented")
