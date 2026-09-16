from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid
from app.models.enums import CVStatus, OrgCandidateStatus

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.profile import CandidateProfile
    from app.models.quiz import Quiz, QuizSubmission
    from app.models.user import User


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id"), unique=True, nullable=True
    )

    # Points at the candidate's CV PDF in Supabase Storage (bucket path,
    # not a full URL) — set once a signed upload completes.
    cv_storage_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cv_status: Mapped[CVStatus] = mapped_column(Enum(CVStatus), default=CVStatus.NONE)
    cv_uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[Optional["User"]] = relationship(back_populates="candidate")
    profiles: Mapped[list["CandidateProfile"]] = relationship(back_populates="candidate")
    org_links: Mapped[list["OrganizationCandidate"]] = relationship(back_populates="candidate")
    quizzes: Mapped[list["Quiz"]] = relationship(back_populates="candidate")
    submissions: Mapped[list["QuizSubmission"]] = relationship(back_populates="candidate")


class OrganizationCandidate(Base, TimestampMixin):
    __tablename__ = "organization_candidates"
    __table_args__ = (UniqueConstraint("organization_id", "candidate_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"))
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("candidates.id"))
    status: Mapped[OrgCandidateStatus] = mapped_column(
        Enum(OrgCandidateStatus), default=OrgCandidateStatus.INVITED
    )
    added_by_user_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )

    organization: Mapped["Organization"] = relationship(back_populates="candidate_links")
    candidate: Mapped["Candidate"] = relationship(back_populates="org_links")
