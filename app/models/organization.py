from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid
from app.models.enums import OrgMemberRole

if TYPE_CHECKING:
    from app.models.candidate import OrganizationCandidate
    from app.models.quiz import Quiz
    from app.models.user import User


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)

    # Total number of quizzes this organization is allowed to create.
    # Enforced at quiz-creation time once quiz generation is implemented.
    quiz_quota: Mapped[int] = mapped_column(Integer, default=0)

    members: Mapped[list["OrganizationMember"]] = relationship(back_populates="organization")
    candidate_links: Mapped[list["OrganizationCandidate"]] = relationship(
        back_populates="organization"
    )
    quizzes: Mapped[list["Quiz"]] = relationship(back_populates="organization")


class OrganizationMember(Base, TimestampMixin):
    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("organization_id", "user_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    role: Mapped[OrgMemberRole] = mapped_column(Enum(OrgMemberRole))

    organization: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="organization_memberships")
