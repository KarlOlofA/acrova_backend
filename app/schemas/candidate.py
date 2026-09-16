from datetime import datetime
from typing import Optional

from app.models.enums import CVStatus, OrgCandidateStatus
from app.schemas.common import ORMModel, TimestampedModel


class CandidateCreate(ORMModel):
    user_id: Optional[str] = None


class CandidateRead(TimestampedModel):
    id: str
    user_id: Optional[str] = None
    cv_status: CVStatus
    cv_storage_path: Optional[str] = None
    cv_uploaded_at: Optional[datetime] = None


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


class CVUploadURLResponse(ORMModel):
    upload_url: str
    token: Optional[str] = None
    storage_path: str


class CVConfirmResponse(ORMModel):
    id: str
    cv_status: CVStatus
    cv_storage_path: Optional[str] = None
    cv_uploaded_at: Optional[datetime] = None
