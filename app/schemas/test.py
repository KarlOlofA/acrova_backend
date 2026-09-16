import uuid

from pydantic import BaseModel, Field


class GeneratedQuestion(BaseModel):
    """Question as produced by Claude — includes the answer key."""

    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str


class GeneratedTest(BaseModel):
    questions: list[GeneratedQuestion] = Field(min_length=5, max_length=8)


class PublicQuestion(BaseModel):
    """Question as shown to the candidate — no answer key."""

    question: str
    options: list[str]


class TestCreateResponse(BaseModel):
    test_id: uuid.UUID


class TestPublic(BaseModel):
    id: uuid.UUID
    questions: list[PublicQuestion]


class TestFromTextRequest(BaseModel):
    text: str


class SubmitRequest(BaseModel):
    answers: list[int]


class SubmitResultDetail(BaseModel):
    question: str
    submitted_index: int | None
    correct_index: int
    is_correct: bool
    explanation: str


class SubmitResponse(BaseModel):
    correct: int
    total: int
    score: float
    details: list[SubmitResultDetail]
