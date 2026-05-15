import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.db.session import get_db
from app.models.chunk import TextChunk
from app.models.document import Document, DocumentPage
from app.schemas.document import ChatRequest, ChatResponse, Citation, DocumentOut
from app.schemas.report import ChronologyItem, ChronologyResponse, ReportRequest, ReportResponse
from app.services.exporter import render_docx, render_pdf
from app.services.parser import chunk_text, extract_pages
from app.services.storage import StorageService

router = APIRouter(dependencies=[Depends(require_api_key)])
storage = StorageService()


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@router.post('/documents', response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Document:
    content = await file.read()
    key = f'uploads/{uuid.uuid4()}-{file.filename}'
    storage.put_bytes(key=key, payload=content, content_type=file.content_type or 'application/octet-stream')

    doc = Document(filename=file.filename, s3_key=key, content_type=file.content_type or 'application/octet-stream')
    db.add(doc)
    db.flush()

    try:
        pages = extract_pages(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    for idx, text in enumerate(pages, start=1):
        db.add(DocumentPage(document_id=doc.id, page_number=idx, text=text))
        for c in chunk_text(text):
            db.add(TextChunk(document_id=doc.id, page_number=idx, text=c))

    db.commit()
    db.refresh(doc)
    return doc


@router.get('/documents', response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return list(db.scalars(select(Document).order_by(Document.created_at.desc())))


def _top_chunks(db: Session, k: int) -> list[TextChunk]:
    return list(db.scalars(select(TextChunk).limit(k)))


def _citations_for_chunks(db: Session, chunks: list[TextChunk]) -> list[Citation]:
    doc_lookup = {d.id: d.filename for d in db.scalars(select(Document).where(Document.id.in_([c.document_id for c in chunks])))}
    return [
        Citation(document_id=c.document_id, filename=doc_lookup.get(c.document_id, 'Unknown'), page_number=c.page_number, chunk_id=c.id)
        for c in chunks
    ]


@router.post('/chat', response_model=ChatResponse)
def chat_with_docs(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    chunks = _top_chunks(db, request.top_k)
    if not chunks:
        raise HTTPException(status_code=400, detail='No indexed documents found.')
    answer = '\n\n'.join([f'- {c.text[:200]}' for c in chunks])
    return ChatResponse(answer=f'Evidence-based answer for: {request.question}\n{answer}', citations=_citations_for_chunks(db, chunks))


@router.post('/chronology', response_model=ChronologyResponse)
def generate_chronology(db: Session = Depends(get_db)) -> ChronologyResponse:
    chunks = _top_chunks(db, 10)
    if not chunks:
        raise HTTPException(status_code=400, detail='No indexed documents found.')
    citations = _citations_for_chunks(db, chunks)
    items = []
    for i, c in enumerate(chunks[:5], start=1):
        items.append(ChronologyItem(date=datetime.utcnow().date().isoformat(), event=f'Event {i}: {c.text[:120]}', citations=[citations[i-1]]))
    return ChronologyResponse(items=items)


@router.post('/reports', response_model=ReportResponse)
def generate_report(request: ReportRequest, db: Session = Depends(get_db)) -> ReportResponse:
    chunks = _top_chunks(db, 8)
    if not chunks:
        raise HTTPException(status_code=400, detail='No indexed documents found.')
    citations = _citations_for_chunks(db, chunks)
    body = f"Format: {request.format}\nPrompt: {request.prompt}\n\n" + '\n'.join([f'* {c.text[:180]}' for c in chunks])
    return ReportResponse(title='Generated Medical-Legal Report', body=body, citations=citations)


@router.post('/reports/export/docx')
def export_report_docx(request: ReportRequest, db: Session = Depends(get_db)) -> Response:
    report = generate_report(request, db)
    payload = render_docx(report.title, report.body)
    return Response(content=payload, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', headers={'Content-Disposition': 'attachment; filename=report.docx'})


@router.post('/reports/export/pdf')
def export_report_pdf(request: ReportRequest, db: Session = Depends(get_db)) -> Response:
    report = generate_report(request, db)
    payload = render_pdf(report.title, report.body)
    return Response(content=payload, media_type='application/pdf', headers={'Content-Disposition': 'attachment; filename=report.pdf'})
