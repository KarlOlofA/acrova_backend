from fastapi import APIRouter, HTTPException

from app.schemas.profile import LinkedInAnalyzeRequest, CandidateProfileRead
from app.services import linkedin_analysis, linkedin_oauth

router = APIRouter(prefix="/auth/linkedin", tags=["auth"])


@router.get("/login")
async def linkedin_login():
    try:
        linkedin_oauth.build_authorization_url()
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.get("/callback")
async def linkedin_callback(code: str):
    try:
        linkedin_oauth.exchange_code_for_token(code)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.post("/analyze", response_model=CandidateProfileRead)
async def linkedin_analyze(payload: LinkedInAnalyzeRequest):
    try:
        linkedin_analysis.fetch_linkedin_profile(access_token="")
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
