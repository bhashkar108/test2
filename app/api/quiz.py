from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, QuizRecord
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/quiz", tags=["Auto Quiz"])

class GenerateQuizRequest(BaseModel):
    topic_or_content: str
    num_questions: Optional[int] = 5
    language: Optional[str] = "en"

class SubmitQuizRequest(BaseModel):
    topic: str
    score: int
    total_questions: int
    questions_data: List[Dict[str, Any]]

@router.post("/generate")
def generate_quiz_endpoint(
    req: GenerateQuizRequest,
    current_user: User = Depends(get_current_user)
):
    if not req.topic_or_content.strip():
        raise HTTPException(status_code=400, detail="Content or topic cannot be empty")

    quiz = gemini_service.generate_quiz(
        content_text=req.topic_or_content,
        num_questions=req.num_questions or 5,
        language=req.language or current_user.language_pref or "en"
    )
    return quiz

@router.post("/submit")
def submit_quiz_endpoint(
    req: SubmitQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = QuizRecord(
        user_id=current_user.id,
        topic=req.topic,
        score=req.score,
        total_questions=req.total_questions,
        questions_data=req.questions_data
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Quiz result recorded successfully",
        "record_id": record.id,
        "score": req.score,
        "total": req.total_questions,
        "percentage": int((req.score / req.total_questions) * 100) if req.total_questions > 0 else 0
    }

@router.get("/history")
def get_quiz_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(QuizRecord).filter(
        QuizRecord.user_id == current_user.id
    ).order_by(QuizRecord.completed_at.desc()).all()

    total_quizzes = len(records)
    total_score = sum(r.score for r in records)
    total_possible = sum(r.total_questions for r in records)
    avg_pct = int((total_score / total_possible * 100)) if total_possible > 0 else 0

    return {
        "total_quizzes": total_quizzes,
        "average_accuracy": avg_pct,
        "records": [
            {
                "id": r.id,
                "topic": r.topic,
                "score": r.score,
                "total_questions": r.total_questions,
                "percentage": int((r.score / r.total_questions) * 100) if r.total_questions > 0 else 0,
                "completed_at": r.completed_at.isoformat() if r.completed_at else ""
            }
            for r in records
        ]
    }
