import os
from pathlib import Path
from typing import Dict, Any, Optional
import pypdf

class DocumentService:
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> Dict[str, Any]:
        """
        Extracts plain text and page count from an uploaded PDF.
        """
        try:
            reader = pypdf.PdfReader(str(file_path))
            num_pages = len(reader.pages)
            text_pages = []
            full_text = []

            for idx, page in enumerate(reader.pages):
                extracted = page.extract_text() or ""
                text_pages.append({"page_number": idx + 1, "text": extracted})
                full_text.append(extracted)

            combined = "\n\n".join(full_text).strip()
            return {
                "success": True,
                "num_pages": num_pages,
                "text": combined,
                "pages": text_pages,
                "char_count": len(combined)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse PDF: {str(e)}",
                "text": "",
                "num_pages": 0
            }

    @staticmethod
    def validate_document(file_path: Path, max_size_mb: int = 25) -> Dict[str, Any]:
        """
        Validates document size, extension, readability.
        """
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        ext = file_path.suffix.lower()

        allowed_exts = [".pdf", ".png", ".jpg", ".jpeg", ".webp"]
        if ext not in allowed_exts:
            return {
                "valid": False,
                "message": f"Unsupported format '{ext}'. Allowed: {', '.join(allowed_exts)}"
            }

        if size_mb > max_size_mb:
            return {
                "valid": False,
                "message": f"File size ({size_mb:.2f}MB) exceeds {max_size_mb}MB limit."
            }

        return {
            "valid": True,
            "size_kb": round(size_bytes / 1024, 2),
            "size_mb": round(size_mb, 2),
            "extension": ext
        }

doc_service = DocumentService()
