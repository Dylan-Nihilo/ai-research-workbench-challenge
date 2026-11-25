from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TaskInput(BaseModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def non_blank_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question cannot be blank")
        return value


class Source(BaseModel):
    id: str
    title: str
    url: str
    excerpt: str
    fetched_at: datetime
    published_at: str | None = None


class Event(BaseModel):
    id: str
    stage: str
    message: str
    created_at: datetime


class ErrorDetail(BaseModel):
    code: str
    message: str


class Task(BaseModel):
    id: str
    question: str
    status: Literal["draft", "queued", "running", "completed", "failed", "cancelled"] = "draft"
    stage: str = "等待开始"
    report: str | None = None
    sources: list[Source] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    error: ErrorDetail | None = None
    created_at: datetime
    updated_at: datetime
