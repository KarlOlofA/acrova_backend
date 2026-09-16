from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.base import utcnow
from app.models.candidate import Candidate
from app.models.enums import QuestionType, QuizStatus, SubmissionStatus
from app.models.organization import Organization
from app.models.profile import CandidateProfile
from app.models.quiz import Quiz, QuizAnswer, QuizQuestion, QuizSubmission
from app.schemas.quiz import QuizCreateRequest, QuizRead, QuizSubmissionRead, QuizSubmitRequest
from app.services import quiz_generation, quiz_scoring

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/")
async def list_quizzes():
    return {"quizzes": []}


@router.post("/create", response_model=QuizRead)
async def create_quiz(payload: QuizCreateRequest, db: Session = Depends(get_db)):
    organization = db.get(Organization, payload.organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    candidate = db.get(Candidate, payload.candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    profile_dict: dict = {}
    if payload.source_profile_id:
        source_profile = db.get(CandidateProfile, payload.source_profile_id)
        if source_profile is None:
            raise HTTPException(status_code=404, detail="Source profile not found")
        profile_dict = {"claims": source_profile.extracted_claims or []}

    try:
        generated = quiz_generation.generate_quiz(
            profile=profile_dict, requirements_spec=payload.requirements_spec
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    quiz = Quiz(
        organization_id=organization.id,
        candidate_id=candidate.id,
        source_profile_id=payload.source_profile_id,
        title=payload.title,
        requirements_spec=payload.requirements_spec,
        status=QuizStatus.GENERATED,
    )
    db.add(quiz)
    db.flush()

    for question in generated["questions"]:
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                order_index=question["order_index"],
                question_text=question["question_text"],
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=question["options"],
                correct_answer=question["correct_answer"],
                skill_tag=question["skill_tag"],
            )
        )

    db.commit()
    db.refresh(quiz)
    return quiz


@router.get("/{quiz_id}", response_model=QuizRead)
async def get_quiz(quiz_id: str, db: Session = Depends(get_db)):
    quiz = db.get(Quiz, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/submit", response_model=QuizSubmissionRead)
async def submit_quiz(payload: QuizSubmitRequest, db: Session = Depends(get_db)):
    quiz = db.get(Quiz, payload.quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz_dict = {
        "questions": [
            {"id": question.id, "correct_answer": question.correct_answer}
            for question in quiz.questions
        ]
    }
    answers = [answer.model_dump() for answer in payload.answers]
    try:
        result = quiz_scoring.score_submission(quiz=quiz_dict, answers=answers)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))

    submission = QuizSubmission(
        quiz_id=quiz.id,
        candidate_id=payload.candidate_id,
        status=SubmissionStatus.SCORED,
        score=result["score"],
        scoring_details=result,
        submitted_at=utcnow(),
    )
    db.add(submission)
    db.flush()

    for detail in result["details"]:
        db.add(
            QuizAnswer(
                submission_id=submission.id,
                question_id=detail["question_id"],
                answer_value={"answer": detail["submitted_answer"]},
                is_correct=detail["is_correct"],
                score_awarded=1.0 if detail["is_correct"] else 0.0,
            )
        )

    db.commit()
    db.refresh(submission)
    return submission


@router.get("/{quiz_id}/results", response_model=QuizSubmissionRead)
async def get_quiz_results(quiz_id: str, db: Session = Depends(get_db)):
    submission = (
        db.query(QuizSubmission)
        .filter_by(quiz_id=quiz_id)
        .order_by(QuizSubmission.created_at.desc())
        .first()
    )
    if submission is None:
        raise HTTPException(status_code=404, detail="No submission found for this quiz")
    return submission
