from app.models.enums import OrgMemberRole
from app.schemas.common import ORMModel, TimestampedModel


class OrganizationCreate(ORMModel):
    name: str
    slug: str


class OrganizationRead(TimestampedModel):
    id: str
    name: str
    slug: str


class OrganizationMemberAdd(ORMModel):
    organization_id: str
    user_id: str
    role: OrgMemberRole


class OrganizationMemberRead(TimestampedModel):
    id: str
    organization_id: str
    user_id: str
    role: OrgMemberRole
