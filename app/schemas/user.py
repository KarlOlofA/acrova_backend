from app.models.enums import UserRole
from app.schemas.common import ORMModel, TimestampedModel


class UserCreate(ORMModel):
    email: str
    full_name: str
    role: UserRole


class UserRead(TimestampedModel):
    id: str
    email: str
    full_name: str
    role: UserRole
