from datetime import datetime
from typing import Optional

from app.models.enums import ProfileSourceType, ProfileStatus
from app.schemas.common import ORMModel, TimestampedModel


class CVAnalyzeRequest(ORMModel):
    candidate_id: str


class CandidateProfileRead(TimestampedModel):
    id: str
    candidate_id: str
    source_type: ProfileSourceType
    status: ProfileStatus
    extracted_claims: Optional[list[dict]] = None
    analyzed_at: Optional[datetime] = None
