from fastapi import APIRouter, HTTPException

from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/user", tags=["users"])


@router.post("/create", response_model=UserRead)
async def create_user(payload: UserCreate):
    raise HTTPException(status_code=501, detail="Creating a user is not yet implemented")


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str):
    raise HTTPException(status_code=501, detail="Fetching a user is not yet implemented")
