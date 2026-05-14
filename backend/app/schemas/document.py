from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    content_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class Citation(BaseModel):
    document_id: UUID
    filename: str
    page_number: int
    chunk_id: int


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
