from pydantic import BaseModel

from app.schemas.document import Citation


class ChronologyItem(BaseModel):
    date: str
    event: str
    citations: list[Citation]


class ChronologyResponse(BaseModel):
    items: list[ChronologyItem]


class ReportRequest(BaseModel):
    prompt: str
    format: str = "narrative"


class ReportResponse(BaseModel):
    title: str
    body: str
    citations: list[Citation]
