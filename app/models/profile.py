from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid
from app.models.enums import ProfileSourceType, ProfileStatus

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.user import User


class CandidateProfile(Base, TimestampMixin):
    """A single CV/LinkedIn/manual analysis record for a candidate.

    ``source_metadata`` holds the source-specific raw payload (raw CV text
    plus file reference, or raw LinkedIn profile JSON). ``extracted_claims``
    is the normalized output consumed by quiz generation, regardless of
    source: a list of ``{skill, evidence, confidence}`` entries.
    """

    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    candidate_id: Mapped[str] = mapped_column(String, ForeignKey("candidates.id"))
    source_type: Mapped[ProfileSourceType] = mapped_column(Enum(ProfileSourceType))
    status: Mapped[ProfileStatus] = mapped_column(Enum(ProfileStatus), default=ProfileStatus.PENDING)
    source_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    extracted_claims: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="profiles")


class LinkedInOAuthToken(Base, TimestampMixin):
    """Seam for the LinkedIn OAuth flow; not wired up yet."""

    __tablename__ = "linkedin_oauth_tokens"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    access_token: Mapped[str] = mapped_column(String)
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scope: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship()
