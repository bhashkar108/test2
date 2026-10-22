from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import shutil
import uuid
from pathlib import Path

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, LearningSession, SmartNote
from app.services.gemini_service import gemini_service
from app.services.doc_service import doc_service

router = APIRouter(prefix="/teacher", tags=["AI Teacher"])

class ExplainRequest(BaseModel):
    text: str
    language: Optional[str] = "en" # en, hi, hinglish
    difficulty: Optional[str] = "medium"
    session_id: Optional[int] = None
    title: Optional[str] = "Study Lesson"

class SaveSessionRequest(BaseModel):
    title: str
    content_type: str = "text"
    source_text: str
    current_index: int = 0
    speed: float = 1.0
    difficulty: str = "medium"
    completed: bool = False

class UpdateSessionRequest(BaseModel):
    current_index: Optional[int] = None
    speed: Optional[float] = None
    completed: Optional[bool] = None

class SaveNoteRequest(BaseModel):
    title: str
    original_snippet: Optional[str] = ""
    teacher_explanation: Optional[str] = ""
    summary: Optional[str] = ""
    key_points: Optional[List[str]] = []
    tags: Optional[str] = "General"

@router.post("/explain")
def get_teacher_explanation(
    req: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    user_lang = req.language or current_user.language_pref or "en"
    explanation_data = gemini_service.explain_step_by_step(
        text=req.text,
        language=user_lang,
        difficulty=req.difficulty or "medium"
    )

    # If session_id provided, update it; otherwise create or update
    session = None
    if req.session_id:
        session = db.query(LearningSession).filter(
            LearningSession.id == req.session_id,
            LearningSession.user_id == current_user.id
        ).first()

    if not session:
        session = LearningSession(
            user_id=current_user.id,
            title=explanation_data.get("title") or req.title or "Study Session",
            content_type="text",
            source_text=req.text[:2000],
            difficulty=req.difficulty or "medium",
            speed=1.0,
            completed=False
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    explanation_data["session_id"] = session.id
    return explanation_data

@router.post("/upload-study-material")
async def upload_study_material(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".txt"]:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported for AI Teacher")

    file_id = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = settings.UPLOAD_DIR / file_id

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = ""
    num_pages = 1
    if ext == ".pdf":
        res = doc_service.extract_text_from_pdf(save_path)
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["error"])
        extracted_text = res["text"]
        num_pages = res["num_pages"]
    else:
        with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
            extracted_text = f.read()

    # Create new learning session
    session = LearningSession(
        user_id=current_user.id,
        title=f"Study: {file.filename}",
        content_type="pdf" if ext == ".pdf" else "text",
        source_text=extracted_text[:3000],
        difficulty="medium"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "filename": file.filename,
        "num_pages": num_pages,
        "text": extracted_text,
        "length": len(extracted_text)
    }

@router.get("/sessions")
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id
    ).order_by(LearningSession.updated_at.desc()).limit(20).all()
    
    return [
        {
            "id": s.id,
            "title": s.title,
            "content_type": s.content_type,
            "current_index": s.current_index,
            "speed": s.speed,
            "difficulty": s.difficulty,
            "completed": s.completed,
            "updated_at": s.updated_at.isoformat() if s.updated_at else s.created_at.isoformat()
        }
        for s in sessions
    ]

@router.put("/sessions/{session_id}")
def update_session_progress(
    session_id: int,
    req: UpdateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if req.current_index is not None:
        session.current_index = req.current_index
    if req.speed is not None:
        session.speed = req.speed
    if req.completed is not None:
        session.completed = req.completed

    db.commit()
    return {"message": "Session updated", "session_id": session.id}

@router.post("/notes")
def save_note(
    req: SaveNoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = SmartNote(
        user_id=current_user.id,
        title=req.title,
        original_snippet=req.original_snippet,
        teacher_explanation=req.teacher_explanation,
        summary=req.summary,
        key_points=req.key_points or [],
        tags=req.tags or "General"
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return {"message": "Note saved successfully", "note_id": note.id}

@router.get("/notes")
def list_notes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notes = db.query(SmartNote).filter(
        SmartNote.user_id == current_user.id
    ).order_by(SmartNote.created_at.desc()).all()
    
    return [
        {
            "id": n.id,
            "title": n.title,
            "original_snippet": n.original_snippet,
            "teacher_explanation": n.teacher_explanation,
            "summary": n.summary,
            "key_points": n.key_points or [],
            "tags": n.tags,
            "created_at": n.created_at.isoformat() if n.created_at else ""
        }
        for n in notes
    ]

@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(SmartNote).filter(
        SmartNote.id == note_id,
        SmartNote.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}
