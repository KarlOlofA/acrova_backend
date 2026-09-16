from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_oauth_state_token,
    decode_oauth_state_token,
)
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.enums import OAuthProvider, UserRole
from app.models.profile import LinkedInOAuthToken
from app.models.user import User
from app.schemas.auth import LinkedInLoginResponse, TokenResponse
from app.schemas.profile import CandidateProfileRead
from app.schemas.user import UserRead
from app.services import linkedin_analysis, linkedin_oauth

router = APIRouter(prefix="/auth/linkedin", tags=["auth"])


@router.get("/login", response_model=LinkedInLoginResponse)
async def linkedin_login(role: UserRole = UserRole.CANDIDATE):
    state = create_oauth_state_token(role=role.value)
    try:
        authorization_url = linkedin_oauth.build_authorization_url(state)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    return LinkedInLoginResponse(authorization_url=authorization_url, state=state)


@router.get("/callback", response_model=TokenResponse)
async def linkedin_callback(code: str, state: str, db: Session = Depends(get_db)):
    try:
        state_payload = decode_oauth_state_token(state)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    try:
        token_data = await linkedin_oauth.exchange_code_for_token(code)
        userinfo = await linkedin_oauth.fetch_linkedin_userinfo(token_data["access_token"])
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    subject = userinfo["sub"]
    email = userinfo.get("email")
    full_name = userinfo.get("name") or email or subject

    user = db.query(User).filter(User.oauth_subject == subject).one_or_none()
    if user is None:
        user = User(
            email=email,
            full_name=full_name,
            role=UserRole(state_payload["role"]),
            oauth_provider=OAuthProvider.LINKEDIN,
            oauth_subject=subject,
        )
        db.add(user)
        db.flush()
        if user.role == UserRole.CANDIDATE:
            db.add(Candidate(user_id=user.id))
        db.commit()
        db.refresh(user)

    expires_in = token_data.get("expires_in", 0)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    token_row = db.query(LinkedInOAuthToken).filter_by(user_id=user.id).one_or_none()
    if token_row is None:
        token_row = LinkedInOAuthToken(user_id=user.id, access_token="", expires_at=expires_at)
        db.add(token_row)
    token_row.access_token = token_data["access_token"]
    token_row.refresh_token = token_data.get("refresh_token")
    token_row.expires_at = expires_at
    token_row.scope = token_data.get("scope")
    db.commit()

    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/analyze", response_model=CandidateProfileRead)
async def linkedin_analyze(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    token_row = db.query(LinkedInOAuthToken).filter_by(user_id=current_user.id).one_or_none()
    if token_row is None:
        raise HTTPException(status_code=400, detail="No LinkedIn account linked for this user")
    try:
        linkedin_analysis.fetch_linkedin_profile(token_row.access_token)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
