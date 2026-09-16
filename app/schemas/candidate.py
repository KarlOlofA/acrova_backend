from typing import Optional

from app.models.enums import OrgCandidateStatus
from app.schemas.common import ORMModel, TimestampedModel


class CandidateCreate(ORMModel):
    user_id: Optional[str] = None


class CandidateRead(TimestampedModel):
    id: str
    user_id: Optional[str] = None


class OrganizationCandidateAdd(ORMModel):
    organization_id: str
    candidate_id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None


class OrganizationCandidateRead(TimestampedModel):
    id: str
    organization_id: str
    candidate_id: str
    status: OrgCandidateStatus
