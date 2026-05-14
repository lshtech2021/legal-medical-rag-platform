from pathlib import Path


def extract_pages(filename: str, payload: bytes) -> list[str]:
    ext = Path(filename).suffix.lower()
    if ext in {".txt", ".md"}:
        return [payload.decode("utf-8", errors="ignore")]
    # Placeholder for OCR/Textract and DOCX/PDF extraction
    return [f"Extracted text placeholder for {filename}"]


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += max(1, size - overlap)
    return chunks
