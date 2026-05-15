# Legal Medical RAG Platform

Internal MVP for legal/medical document analysis with citation-aware outputs.

## Implemented Features
- Secure internal API key auth (`x-api-key`) for backend endpoints.
- Upload PDF, DOCX, TXT/MD, and image files.
- Text extraction pipeline:
  - PDF parsing via `pypdf`
  - DOCX parsing via `python-docx`
  - Image OCR via `pytesseract`
- Source tracking persistence by document, page, and chunk in PostgreSQL.
- Citation-aware chat endpoint.
- Medical chronology generation endpoint with citations.
- Structured report generation endpoint with citations.
- Export report to DOCX and PDF.
- Frontend actions for upload, chat, chronology, report generation, export, and copy-to-clipboard.

## Backend API
- `GET /api/v1/health`
- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `POST /api/v1/chat`
- `POST /api/v1/chronology`
- `POST /api/v1/reports`
- `POST /api/v1/reports/export/docx`
- `POST /api/v1/reports/export/pdf`

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
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 NEXT_PUBLIC_INTERNAL_API_KEY=dev-internal-key npm run dev
```

## OCR system dependency
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr
```
