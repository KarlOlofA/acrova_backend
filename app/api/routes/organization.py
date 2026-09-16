from fastapi import APIRouter, HTTPException

from app.schemas.candidate import OrganizationCandidateAdd, OrganizationCandidateRead
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organization", tags=["organizations"])


@router.post("/create", response_model=OrganizationRead)
async def create_organization(payload: OrganizationCreate):
    raise HTTPException(status_code=501, detail="Creating an organization is not yet implemented")


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(org_id: str):
    raise HTTPException(status_code=501, detail="Fetching an organization is not yet implemented")


@router.post("/candidate/add", response_model=OrganizationCandidateRead)
async def add_candidate(payload: OrganizationCandidateAdd):
    raise HTTPException(
        status_code=501, detail="Adding a candidate to an organization is not yet implemented"
    )


@router.get("/{org_id}/candidates")
async def list_organization_candidates(org_id: str):
    return {"candidates": []}
