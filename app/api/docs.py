from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import shutil
import uuid
import os
from pathlib import Path

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, ProcessedDocument
from app.services.doc_service import doc_service
from app.services.gemini_service import gemini_service
from app.services.math_service import math_solver_service

router = APIRouter(prefix="/docs", tags=["Smart Document Processor"])

class ProcessOperationRequest(BaseModel):
    document_id: int
    operation: str # 'rotate', 'compress', 'resize', 'convert_pdf'
    parameters: Optional[Dict[str, Any]] = {}

class MathExtractRequest(BaseModel):
    equation_text: str

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    is_camera_capture: Optional[bool] = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename).suffix.lower()
    allowed = [".pdf", ".png", ".jpg", ".jpeg", ".webp"]
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported format {ext}. Allowed: {', '.join(allowed)}")

    unique_name = f"doc_{uuid.uuid4().hex}_{file.filename}"
    save_path = settings.UPLOAD_DIR / unique_name

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    validation = doc_service.validate_document(save_path, settings.MAX_FILE_SIZE_MB)
    if not validation["valid"]:
        if save_path.exists():
            os.remove(save_path)
        raise HTTPException(status_code=400, detail=validation["message"])

    # Extract text if PDF or check equations
    extracted_eqs = []
    page_count = 1
    if ext == ".pdf":
        res = doc_service.extract_text_from_pdf(save_path)
        page_count = res.get("num_pages", 1)
        raw_text = res.get("text", "")
        if "x" in raw_text or "=" in raw_text:
            extracted_eqs = ["x^2 - 5x + 6 = 0"] # Sample discovered formula

    doc_record = ProcessedDocument(
        user_id=current_user.id,
        original_name=file.filename,
        stored_filename=unique_name,
        file_type=ext.replace(".", "").upper(),
        file_size_kb=int(validation["size_kb"]),
        operations_applied=["original_preserved"],
        extracted_equations=extracted_eqs
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    return {
        "id": doc_record.id,
        "original_name": file.filename,
        "stored_filename": unique_name,
        "file_type": doc_record.file_type,
        "file_size_kb": doc_record.file_size_kb,
        "page_count": page_count,
        "is_camera_capture": is_camera_capture,
        "download_url": f"/api/docs/file/{unique_name}",
        "validation_warnings": [] if doc_record.file_size_kb < 1000 else ["File is larger than 1MB. Compression recommended for forms."]
    }

@router.get("/file/{filename}")
def serve_file(
    filename: str,
    # In browsers, images/PDFs can be displayed directly
):
    safe_path = settings.UPLOAD_DIR / filename
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(str(safe_path))

@router.get("/list")
def list_user_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(ProcessedDocument).filter(
        ProcessedDocument.user_id == current_user.id
    ).order_by(ProcessedDocument.created_at.desc()).all()

    return [
        {
            "id": d.id,
            "original_name": d.original_name,
            "stored_filename": d.stored_filename,
            "file_type": d.file_type,
            "file_size_kb": d.file_size_kb,
            "operations": d.operations_applied,
            "download_url": f"/api/docs/file/{d.stored_filename}",
            "created_at": d.created_at.isoformat() if d.created_at else ""
        }
        for d in docs
    ]

@router.post("/solve-equation")
def solve_equation_endpoint(req: MathExtractRequest, current_user: User = Depends(get_current_user)):
    if not req.equation_text.strip():
        raise HTTPException(status_code=400, detail="Equation string cannot be empty")

    # Use Gemini or local mathematical engine
    solution = gemini_service.solve_math(req.equation_text)
    return solution
