import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.test import Test
from app.schemas.test import (
    PublicQuestion,
    SubmitRequest,
    SubmitResponse,
    SubmitResultDetail,
    TestCreateResponse,
    TestPublic,
)
from app.services.claude_service import generate_test_from_cv

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/from-cv", response_model=TestCreateResponse)
async def create_test_from_cv(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    cv_text: str | None = None
    pdf_bytes: bytes | None = None

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file")
        if upload is None:
            raise HTTPException(status_code=400, detail="Missing 'file' in form-data")
        pdf_bytes = await upload.read()
    elif content_type.startswith("application/json"):
        body = await request.json()
        cv_text = body.get("text")
        if not cv_text:
            raise HTTPException(status_code=400, detail="Missing 'text' in JSON body")
    else:
        raise HTTPException(
            status_code=415,
            detail="Content-Type must be multipart/form-data (file) or application/json (text)",
        )

    try:
        generated = generate_test_from_cv(cv_text=cv_text, pdf_bytes=pdf_bytes)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to generate test: {exc}") from exc

    test = Test(questions=[q.model_dump() for q in generated.questions])
    db.add(test)
    db.commit()
    db.refresh(test)

    return TestCreateResponse(test_id=test.id)


@router.get("/{test_id}", response_model=TestPublic)
def get_test(test_id: uuid.UUID, db: Session = Depends(get_db)):
    test = db.get(Test, test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")

    questions = [
        PublicQuestion(question=q["question"], options=q["options"]) for q in test.questions
    ]
    return TestPublic(id=test.id, questions=questions)


@router.post("/{test_id}/submit", response_model=SubmitResponse)
def submit_test(test_id: uuid.UUID, submission: SubmitRequest, db: Session = Depends(get_db)):
    test = db.get(Test, test_id)
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")

    questions = test.questions
    if len(submission.answers) != len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(questions)} answers, got {len(submission.answers)}",
        )

    details = []
    correct_count = 0
    for question, submitted_index in zip(questions, submission.answers):
        is_correct = submitted_index == question["correct_index"]
        if is_correct:
            correct_count += 1
        details.append(
            SubmitResultDetail(
                question=question["question"],
                submitted_index=submitted_index,
                correct_index=question["correct_index"],
                is_correct=is_correct,
                explanation=question["explanation"],
            )
        )

    total = len(questions)
    return SubmitResponse(
        correct=correct_count,
        total=total,
        score=round(correct_count / total, 4) if total else 0.0,
        details=details,
    )
