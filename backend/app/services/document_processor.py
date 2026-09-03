import io
import logging
from typing import List, Dict, Any, Optional
import pypdf
import docx
from app.services.text_cleaner import text_cleaner

logger = logging.getLogger("ventureos.document_processor")


class DocumentProcessor:
    """
    Extracts raw text and metadata from PDF, DOCX, TXT, and Markdown files.
    """

    def extract(self, file_bytes: bytes, filename: str, file_type: str) -> List[Dict[str, Any]]:
        """
        Extracts content into structured blocks (page-aware where applicable).
        Returns:
            List of dicts: [{"text": str, "page": Optional[int], "source": str}]
        """
        ext = self._detect_extension(filename, file_type)
        logger.info("Extracting text from file: '%s' (detected extension: %s, size: %d bytes)", filename, ext, len(file_bytes))

        if ext == "pdf":
            return self._extract_pdf(file_bytes, filename)
        elif ext == "docx":
            return self._extract_docx(file_bytes, filename)
        elif ext in ("txt", "md", "markdown"):
            return self._extract_text(file_bytes, filename)
        else:
            raise ValueError(f"Unsupported file format: '.{ext}'. Supported formats are: PDF, DOCX, TXT, MD.")

    def _detect_extension(self, filename: str, file_type: str) -> str:
        parts = filename.lower().rsplit(".", 1)
        if len(parts) > 1:
            return parts[1]
        
        # Fallback to MIME type mapping
        mime = file_type.lower()
        if "pdf" in mime:
            return "pdf"
        elif "wordprocessingml" in mime or "docx" in mime:
            return "docx"
        elif "markdown" in mime:
            return "md"
        elif "text" in mime:
            return "txt"
        return "unknown"

    def _extract_pdf(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        blocks: List[Dict[str, Any]] = []
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            logger.info("PDF '%s' has %d pages", filename, total_pages)

            for page_num, page in enumerate(reader.pages, start=1):
                raw_text = page.extract_text() or ""
                cleaned = text_cleaner.clean(raw_text)
                if cleaned:
                    blocks.append({
                        "text": cleaned,
                        "page": page_num,
                        "source": filename,
                    })

            if not blocks:
                raise ValueError("PDF contains no extractable text. It may consist solely of scanned images.")

            return blocks
        except Exception as e:
            logger.error("Failed to extract PDF '%s': %s", filename, str(e))
            raise ValueError(f"Failed to process PDF: {str(e)}")

    def _extract_docx(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            full_paragraphs = []
            for p in doc.paragraphs:
                text = p.text.strip()
                if text:
                    full_paragraphs.append(text)

            combined_text = "\n\n".join(full_paragraphs)
            cleaned = text_cleaner.clean(combined_text)
            if not cleaned:
                raise ValueError("DOCX contains no extractable text.")

            return [{
                "text": cleaned,
                "page": None,
                "source": filename,
            }]
        except Exception as e:
            logger.error("Failed to extract DOCX '%s': %s", filename, str(e))
            raise ValueError(f"Failed to process DOCX: {str(e)}")

    def _extract_text(self, file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        try:
            try:
                decoded = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                decoded = file_bytes.decode("latin-1")

            cleaned = text_cleaner.clean(decoded)
            if not cleaned:
                raise ValueError("Text document is empty.")

            return [{
                "text": cleaned,
                "page": None,
                "source": filename,
            }]
        except Exception as e:
            logger.error("Failed to extract text document '%s': %s", filename, str(e))
            raise ValueError(f"Failed to process text file: {str(e)}")


document_processor = DocumentProcessor()
