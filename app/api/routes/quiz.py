from fastapi import APIRouter, HTTPException

from app.schemas.quiz import QuizCreateRequest, QuizRead, QuizSubmissionRead, QuizSubmitRequest
from app.services import quiz_generation, quiz_scoring

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/")
async def list_quizzes():
    return {"quizzes": []}


@router.post("/create", response_model=QuizRead)
async def create_quiz(payload: QuizCreateRequest):
    try:
        quiz_generation.generate_quiz(
            profile={}, requirements_spec=payload.requirements_spec
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.get("/{quiz_id}", response_model=QuizRead)
async def get_quiz(quiz_id: str):
    raise HTTPException(status_code=501, detail="Fetching a quiz is not yet implemented")


@router.post("/submit", response_model=QuizSubmissionRead)
async def submit_quiz(payload: QuizSubmitRequest):
    try:
        quiz_scoring.score_submission(quiz={}, answers=[a.model_dump() for a in payload.answers])
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.get("/{quiz_id}/results", response_model=QuizSubmissionRead)
async def get_quiz_results(quiz_id: str):
    raise HTTPException(status_code=501, detail="Fetching quiz results is not yet implemented")
