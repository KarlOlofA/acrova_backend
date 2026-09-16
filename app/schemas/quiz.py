from datetime import datetime
from typing import Optional

from app.models.enums import QuestionType, QuizStatus, SubmissionStatus
from app.schemas.common import ORMModel, TimestampedModel


class QuizCreateRequest(ORMModel):
    organization_id: str
    candidate_id: str
    source_profile_id: Optional[str] = None
    title: str
    requirements_spec: dict


class QuizQuestionRead(ORMModel):
    """Candidate-facing question shape; deliberately omits correct_answer."""

    id: str
    order_index: int
    question_text: str
    question_type: QuestionType
    options: Optional[dict] = None
    skill_tag: Optional[str] = None


class QuizRead(TimestampedModel):
    id: str
    organization_id: str
    candidate_id: str
    source_profile_id: Optional[str] = None
    title: str
    status: QuizStatus
    questions: list[QuizQuestionRead] = []


class QuizAnswerIn(ORMModel):
    question_id: str
    answer_value: dict


class QuizSubmitRequest(ORMModel):
    quiz_id: str
    candidate_id: str
    answers: list[QuizAnswerIn]


class QuizSubmissionRead(TimestampedModel):
    id: str
    quiz_id: str
    candidate_id: str
    status: SubmissionStatus
    score: Optional[float] = None
    submitted_at: Optional[datetime] = None
