from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid
from app.models.enums import QuestionType, QuizStatus, SubmissionStatus

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.organization import Organization
    from app.models.profile import CandidateProfile


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"))
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("candidates.id"))
    source_profile_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("candidate_profiles.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String)
    requirements_spec: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[QuizStatus] = mapped_column(Enum(QuizStatus), default=QuizStatus.DRAFT)

    organization: Mapped["Organization"] = relationship(back_populates="quizzes")
    candidate: Mapped["Candidate"] = relationship(back_populates="quizzes")
    source_profile: Mapped[Optional["CandidateProfile"]] = relationship()
    questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="quiz", order_by="QuizQuestion.order_index"
    )
    submissions: Mapped[list["QuizSubmission"]] = relationship(back_populates="quiz")


class QuizQuestion(Base, TimestampMixin):
    __tablename__ = "quiz_questions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    quiz_id: Mapped[str] = mapped_column(String, ForeignKey("quizzes.id"))
    order_index: Mapped[int] = mapped_column(Integer)
    question_text: Mapped[str] = mapped_column(String)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType))
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    skill_tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")


class QuizSubmission(Base, TimestampMixin):
    __tablename__ = "quiz_submissions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    quiz_id: Mapped[str] = mapped_column(String, ForeignKey("quizzes.id"))
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("candidates.id"))
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), default=SubmissionStatus.IN_PROGRESS
    )
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    scoring_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    quiz: Mapped["Quiz"] = relationship(back_populates="submissions")
    candidate: Mapped["Candidate"] = relationship(back_populates="submissions")
    answers: Mapped[list["QuizAnswer"]] = relationship(back_populates="submission")


class QuizAnswer(Base, TimestampMixin):
    __tablename__ = "quiz_answers"
    __table_args__ = (UniqueConstraint("submission_id", "question_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    submission_id: Mapped[str] = mapped_column(String, ForeignKey("quiz_submissions.id"))
    question_id: Mapped[str] = mapped_column(String, ForeignKey("quiz_questions.id"))
    answer_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(nullable=True)
    score_awarded: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    submission: Mapped["QuizSubmission"] = relationship(back_populates="answers")
