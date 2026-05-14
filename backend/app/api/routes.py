import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chunk import TextChunk
from app.models.document import Document, DocumentPage
from app.schemas.document import ChatRequest, ChatResponse, Citation, DocumentOut
from app.services.parser import chunk_text, extract_pages
from app.services.storage import StorageService

router = APIRouter()
storage = StorageService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/documents", response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Document:
    content = await file.read()
    key = f"uploads/{uuid.uuid4()}-{file.filename}"
    storage.put_bytes(key=key, payload=content, content_type=file.content_type or "application/octet-stream")

    doc = Document(filename=file.filename, s3_key=key, content_type=file.content_type or "application/octet-stream")
    db.add(doc)
    db.flush()

    pages = extract_pages(file.filename, content)
    for idx, text in enumerate(pages, start=1):
        db.add(DocumentPage(document_id=doc.id, page_number=idx, text=text))
        for c in chunk_text(text):
            db.add(TextChunk(document_id=doc.id, page_number=idx, text=c))

    db.commit()
    db.refresh(doc)
    return doc


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return list(db.scalars(select(Document).order_by(Document.created_at.desc())))


@router.post("/chat", response_model=ChatResponse)
def chat_with_docs(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    chunks = list(db.scalars(select(TextChunk).limit(request.top_k)))
    if not chunks:
        raise HTTPException(status_code=400, detail="No indexed documents found.")

    answer = "\n\n".join([f"- {c.text[:200]}" for c in chunks])
    doc_lookup = {d.id: d.filename for d in db.scalars(select(Document).where(Document.id.in_([c.document_id for c in chunks])))}
    citations = [
        Citation(
            document_id=c.document_id,
            filename=doc_lookup.get(c.document_id, "Unknown"),
            page_number=c.page_number,
            chunk_id=c.id,
        )
        for c in chunks
    ]
    return ChatResponse(answer=f"Evidence-based draft answer for: {request.question}\n{answer}", citations=citations)
