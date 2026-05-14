# Legal Medical RAG Platform

Phased MVP implementation:

## Phase 1: Backend + Frontend Foundation
- FastAPI + SQLAlchemy project scaffold
- Next.js app scaffold
- Shared API contract for documents/chat/citations

## Phase 2: Backend Implementation
- Document upload endpoint with S3 storage abstraction
- Parsing/OCR placeholder service
- Page + chunk persistence for source tracking
- Chat endpoint returning citation objects

## Phase 3: Frontend Implementation
- Upload UI
- Document list UI
- Chat UI with citations
- Copy-to-clipboard for generated output

## Run backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run frontend
```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 npm run dev
```
