from fastapi import APIRouter, HTTPException

from app.schemas.candidate import CandidateCreate, CandidateRead

router = APIRouter(prefix="/candidate", tags=["candidates"])


@router.post("/create", response_model=CandidateRead)
async def create_candidate(payload: CandidateCreate):
    raise HTTPException(status_code=501, detail="Creating a candidate is not yet implemented")


@router.get("/{candidate_id}", response_model=CandidateRead)
async def get_candidate(candidate_id: str):
    raise HTTPException(status_code=501, detail="Fetching a candidate is not yet implemented")


@router.get("/{candidate_id}/profiles")
async def list_candidate_profiles(candidate_id: str):
    return {"profiles": []}
