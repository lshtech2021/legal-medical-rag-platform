from __future__ import annotations

import io
from pathlib import Path

from docx import Document as DocxDocument
from PIL import Image
from pypdf import PdfReader


def _extract_pdf_pages(payload: bytes) -> list[str]:
    reader = PdfReader(io.BytesIO(payload))
    pages: list[str] = []
    for page in reader.pages:
        pages.append((page.extract_text() or "").strip())
    return pages


def _extract_docx_text(payload: bytes) -> list[str]:
    doc = DocxDocument(io.BytesIO(payload))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return ["\n".join(paragraphs)] if paragraphs else [""]


def _extract_plain_text(payload: bytes) -> list[str]:
    return [payload.decode("utf-8", errors="ignore")]


def _extract_image_ocr(payload: bytes) -> list[str]:
    try:
        import pytesseract
    except Exception as exc:  # pragma: no cover - runtime dependency guard
        raise RuntimeError(
            "Image OCR requires pytesseract and system tesseract installed. "
            "Install pytesseract and tesseract-ocr to enable local OCR."
        ) from exc

    img = Image.open(io.BytesIO(payload))
    text = pytesseract.image_to_string(img)
    return [text.strip()]


def extract_pages(filename: str, payload: bytes) -> list[str]:
    ext = Path(filename).suffix.lower()

    if ext == ".pdf":
        pages = _extract_pdf_pages(payload)
    elif ext == ".docx":
        pages = _extract_docx_text(payload)
    elif ext in {".txt", ".md"}:
        pages = _extract_plain_text(payload)
    elif ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}:
        pages = _extract_image_ocr(payload)
    else:
        raise ValueError(f"Unsupported file extension: {ext or 'unknown'}")

    cleaned = [page.strip() for page in pages if page and page.strip()]
    return cleaned or [""]


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += max(1, size - overlap)
    return chunks
