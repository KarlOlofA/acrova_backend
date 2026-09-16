from fastapi import APIRouter

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/")
async def list_quizzes():
    return {"quizzes": []}
