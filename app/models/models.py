import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(191), unique=True, index=True, nullable=False)
    full_name = Column(String(191), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="student")
    language_pref = Column(String(20), default="en") # en, hi, hinglish
    theme_pref = Column(String(20), default="dark") # dark, light
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("SmartNote", back_populates="user", cascade="all, delete-orphan")
    forms = relationship("FormAnalysis", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("ProcessedDocument", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("QuizRecord", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(100), nullable=True)
    father_name = Column(String(191), nullable=True)
    mother_name = Column(String(191), nullable=True)
    dob = Column(String(50), nullable=True)
    gender = Column(String(30), nullable=True)
    category = Column(String(50), default="General") # General, OBC, SC, ST, EWS
    village = Column(String(191), nullable=True)
    district = Column(String(191), nullable=True)
    state = Column(String(191), nullable=True)
    pin_code = Column(String(20), nullable=True)
    college = Column(String(255), nullable=True)
    branch = Column(String(191), nullable=True)
    section = Column(String(50), nullable=True)
    academic_year = Column(String(50), nullable=True)
    phone_number = Column(String(30), nullable=True)
    annual_income = Column(String(50), nullable=True)
    aadhar_last4 = Column(String(10), nullable=True)
    bank_account = Column(String(100), nullable=True)
    ifsc_code = Column(String(50), nullable=True)
    verified_docs_meta = Column(JSON, default=dict)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), default="pdf") # pdf, text, notes
    source_text = Column(Text, nullable=True)
    current_index = Column(Integer, default=0)
    speed = Column(Float, default=1.0)
    difficulty = Column(String(50), default="medium")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="sessions")


class SmartNote(Base):
    __tablename__ = "smart_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    original_snippet = Column(Text, nullable=True)
    teacher_explanation = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    key_points = Column(JSON, default=list)
    tags = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notes")


class FormAnalysis(Base):
    __tablename__ = "form_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    form_source = Column(String(255), nullable=True)
    detected_fields = Column(JSON, default=list)
    matched_profile = Column(JSON, default=dict)
    missing_fields = Column(JSON, default=list)
    document_requirements = Column(JSON, default=list)
    status = Column(String(50), default="analyzed") # analyzed, prepared, exported
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="forms")


class ProcessedDocument(Base):
    __tablename__ = "processed_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_name = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)
    file_size_kb = Column(Integer, default=0)
    operations_applied = Column(JSON, default=list)
    extracted_equations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="documents")


class QuizRecord(Base):
    __tablename__ = "quiz_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(255), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    questions_data = Column(JSON, default=list)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="quizzes")
