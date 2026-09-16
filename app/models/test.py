from sqlalchemy import Column, DateTime, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.core.db import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    candidate_name = Column(Text, nullable=True)
    cv_storage_path = Column(Text, nullable=True)
    cv_text = Column(Text, nullable=True)
    questions = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
