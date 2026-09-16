from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid
from app.models.enums import OAuthProvider, UserRole

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.organization import OrganizationMember


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))

    oauth_provider: Mapped[Optional[OAuthProvider]] = mapped_column(
        Enum(OAuthProvider), nullable=True
    )
    oauth_subject: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    candidate: Mapped[Optional["Candidate"]] = relationship(back_populates="user", uselist=False)
    organization_memberships: Mapped[list["OrganizationMember"]] = relationship(
        back_populates="user"
    )
