from app.models.enums import OrgMemberRole
from app.schemas.common import ORMModel, TimestampedModel


class OrganizationCreate(ORMModel):
    name: str
    slug: str
    quiz_quota: int = 0


class OrganizationRead(TimestampedModel):
    id: str
    name: str
    slug: str
    quiz_quota: int


class OrganizationMemberAdd(ORMModel):
    organization_id: str
    user_id: str
    role: OrgMemberRole


class OrganizationMemberRead(TimestampedModel):
    id: str
    organization_id: str
    user_id: str
    role: OrgMemberRole
