from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.candidate import Candidate, OrganizationCandidate
from app.models.enums import OrgMemberRole, UserRole
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.schemas.candidate import OrganizationCandidateAdd, OrganizationCandidateRead
from app.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organization", tags=["organizations"])


@router.post("/create", response_model=OrganizationRead, status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.RECRUITER:
        raise HTTPException(status_code=403, detail="Only recruiters can create organizations")
    if db.query(Organization).filter(Organization.slug == payload.slug).first():
        raise HTTPException(
            status_code=409, detail="An organization with this slug already exists"
        )
    org = Organization(name=payload.name, slug=payload.slug, quiz_quota=payload.quiz_quota)
    db.add(org)
    db.flush()
    db.add(
        OrganizationMember(
            organization_id=org.id, user_id=current_user.id, role=OrgMemberRole.OWNER
        )
    )
    db.commit()
    db.refresh(org)
    return org


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(org_id: str, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.post("/candidate/add", response_model=OrganizationCandidateRead, status_code=201)
async def add_candidate(
    payload: OrganizationCandidateAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org = db.get(Organization, payload.organization_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    is_member = (
        db.query(OrganizationMember)
        .filter_by(organization_id=org.id, user_id=current_user.id)
        .first()
    )
    if is_member is None:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    if payload.candidate_id:
        candidate = db.get(Candidate, payload.candidate_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
    elif payload.email:
        user = db.query(User).filter(User.email == payload.email).one_or_none()
        if user is None:
            user = User(
                email=payload.email,
                full_name=payload.full_name or payload.email,
                role=UserRole.CANDIDATE,
            )
            db.add(user)
            db.flush()
        candidate = user.candidate
        if candidate is None:
            candidate = Candidate(user_id=user.id)
            db.add(candidate)
            db.flush()
    else:
        raise HTTPException(status_code=400, detail="Provide either candidate_id or email")

    existing_link = (
        db.query(OrganizationCandidate)
        .filter_by(organization_id=org.id, candidate_id=candidate.id)
        .first()
    )
    if existing_link:
        raise HTTPException(
            status_code=409, detail="Candidate is already linked to this organization"
        )

    link = OrganizationCandidate(
        organization_id=org.id, candidate_id=candidate.id, added_by_user_id=current_user.id
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.get("/{org_id}/candidates")
async def list_organization_candidates(org_id: str, db: Session = Depends(get_db)):
    links = db.query(OrganizationCandidate).filter_by(organization_id=org_id).all()
    return {"candidates": [OrganizationCandidateRead.model_validate(link) for link in links]}
