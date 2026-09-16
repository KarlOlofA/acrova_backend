from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import UserRole
from app.models.candidate import Candidate
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/user", tags=["users"])


@router.post("/create", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="A user with this email already exists")
    user = User(email=payload.email, full_name=payload.full_name, role=payload.role)
    db.add(user)
    db.flush()
    if user.role == UserRole.CANDIDATE:
        db.add(Candidate(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
