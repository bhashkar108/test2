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
from app.models.models import User, UserProfile, FormAnalysis
from app.services.gemini_service import gemini_service
from app.services.doc_service import doc_service

router = APIRouter(prefix="/forms", tags=["Auto Form Filler"])

class AnalyzeUrlRequest(BaseModel):
    url: Optional[str] = None
    form_title: Optional[str] = "Online Admission / Scholarship Portal"
    raw_text: Optional[str] = None

class FormSubmissionRequest(BaseModel):
    analysis_id: Optional[int] = None
    form_title: str
    filled_data: Dict[str, Any]
    status: Optional[str] = "completed"

@router.post("/analyze-form")
async def analyze_form(
    file: Optional[UploadFile] = File(None),
    form_url: Optional[str] = Form(None),
    form_text: Optional[str] = Form(None),
    form_title: Optional[str] = Form("Student Application Form"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    extracted_text = ""
    source_label = form_title

    if file:
        ext = Path(file.filename).suffix.lower()
        file_id = f"form_{uuid.uuid4().hex}_{file.filename}"
        save_path = settings.UPLOAD_DIR / file_id
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if ext == ".pdf":
            res = doc_service.extract_text_from_pdf(save_path)
            extracted_text = res.get("text", "")
        else:
            extracted_text = f"Form Image: {file.filename}. Standard Indian College / Scholarship Application form."
        source_label = file.filename
    elif form_text:
        extracted_text = form_text
    elif form_url:
        extracted_text = f"Application portal at {form_url}. Standard National Scholarship / University Admission form requirements."
        source_label = form_url
    else:
        extracted_text = "Standard All India College & Scholarship Application form requirements."

    # 1. Analyze form and instructions BEFORE asking student
    analysis_result = gemini_service.analyze_form(
        form_text=extracted_text,
        form_title=source_label
    )

    # 2. Retrieve student's saved profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    profile_dict = {}
    if profile:
        profile_dict = {
            "student_name": current_user.full_name or "",
            "roll_number": profile.roll_number or "",
            "father_name": profile.father_name or "",
            "mother_name": profile.mother_name or "",
            "dob": profile.dob or "",
            "gender": profile.gender or "",
            "category": profile.category or "General",
            "village": profile.village or "",
            "district": profile.district or "",
            "state": profile.state or "",
            "pin_code": profile.pin_code or "",
            "college": profile.college or "",
            "branch": profile.branch or "",
            "section": profile.section or "",
            "academic_year": profile.academic_year or "",
            "phone_number": profile.phone_number or "",
            "annual_income": profile.annual_income or "",
            "aadhar_last4": profile.aadhar_last4 or "",
            "bank_account": profile.bank_account or "",
            "ifsc_code": profile.ifsc_code or "",
        }
    else:
        profile_dict = {
            "student_name": current_user.full_name or ""
        }

    # 3. Compare requirements with student's profile (Reuse verified info, identify missing)
    required_fields = analysis_result.get("required_fields", [])
    matched_data = {}
    missing_fields = []
    completed_fields = []

    for f in required_fields:
        fid = f.get("field_id")
        label = f.get("label", fid)
        val = profile_dict.get(fid, "")
        if val and str(val).strip():
            matched_data[fid] = val
            completed_fields.append({
                "field_id": fid,
                "label": label,
                "value": val,
                "status": "verified"
            })
        else:
            missing_fields.append({
                "field_id": fid,
                "label": label,
                "required": f.get("required", True),
                "type": f.get("type", "text")
            })

    # Save to database
    analysis_record = FormAnalysis(
        user_id=current_user.id,
        title=analysis_result.get("form_title", source_label),
        form_source=source_label,
        detected_fields=required_fields,
        matched_profile=matched_data,
        missing_fields=missing_fields,
        document_requirements=analysis_result.get("document_requirements", []),
        status="analyzed"
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    total_fields = len(required_fields)
    completion_pct = int((len(completed_fields) / total_fields * 100)) if total_fields > 0 else 0

    return {
        "analysis_id": analysis_record.id,
        "form_title": analysis_result.get("form_title", source_label),
        "form_category": analysis_result.get("form_category", "Student Application"),
        "eligibility_summary": analysis_result.get("eligibility_summary", ""),
        "total_fields_count": total_fields,
        "completed_count": len(completed_fields),
        "missing_count": len(missing_fields),
        "completion_percentage": completion_pct,
        "completed_fields": completed_fields,
        "missing_fields": missing_fields,
        "matched_data": matched_data,
        "document_requirements": analysis_result.get("document_requirements", []),
        "important_warnings": analysis_result.get("important_warnings", [])
    }

@router.post("/save-filled")
def save_filled_form(
    req: FormSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if req.analysis_id:
        record = db.query(FormAnalysis).filter(
            FormAnalysis.id == req.analysis_id,
            FormAnalysis.user_id == current_user.id
        ).first()
        if record:
            record.matched_profile = req.filled_data
            record.status = "completed"
            db.commit()

    # Also automatically sync filled info into user profile for future forms!
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    for key, val in req.filled_data.items():
        if hasattr(profile, key) and val:
            setattr(profile, key, str(val))

    db.commit()
    return {"message": "Form saved and profile updated successfully", "form_title": req.form_title}

@router.get("/history")
def get_forms_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(FormAnalysis).filter(
        FormAnalysis.user_id == current_user.id
    ).order_by(FormAnalysis.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "title": r.title,
            "form_source": r.form_source,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else ""
        }
        for r in records
    ]
