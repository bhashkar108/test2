from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.models import User, UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    language_pref: Optional[str] = "en"
    theme_pref: Optional[str] = "dark"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    roll_number: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[str] = "General"
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    section: Optional[str] = None
    academic_year: Optional[str] = None
    phone_number: Optional[str] = None
    annual_income: Optional[str] = None
    aadhar_last4: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None

class PreferencesRequest(BaseModel):
    language_pref: Optional[str] = None
    theme_pref: Optional[str] = None

@router.post("/register")
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = hash_password(req.password)
    user = User(
        email=req.email.lower(),
        full_name=req.full_name,
        hashed_password=hashed_pw,
        language_pref=req.language_pref or "en",
        theme_pref=req.theme_pref or "dark"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize associated student profile
    profile = UserProfile(
        user_id=user.id,
        category="General"
    )
    db.add(profile)
    db.commit()

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "language_pref": user.language_pref,
            "theme_pref": user.theme_pref
        }
    }

@router.post("/login")
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "language_pref": user.language_pref,
            "theme_pref": user.theme_pref
        }
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    profile_data = {}
    if profile:
        profile_data = {
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

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "language_pref": current_user.language_pref,
            "theme_pref": current_user.theme_pref,
        },
        "profile": profile_data
    }

@router.put("/profile")
def update_profile(req: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    update_dict = req.dict(exclude_unset=True)
    for key, val in update_dict.items():
        setattr(profile, key, val)

    db.commit()
    return {"message": "Profile updated successfully", "profile": update_dict}

@router.put("/preferences")
def update_preferences(req: PreferencesRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.language_pref:
        current_user.language_pref = req.language_pref
    if req.theme_pref:
        current_user.theme_pref = req.theme_pref

    db.commit()
    return {"message": "Preferences saved", "language_pref": current_user.language_pref, "theme_pref": current_user.theme_pref}
