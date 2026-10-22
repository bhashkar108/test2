import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.models import User, UserProfile
from app.core.security import hash_password

# API Routers
from app.api.auth import router as auth_router
from app.api.teacher import router as teacher_router
from app.api.forms import router as forms_router
from app.api.docs import router as docs_router
from app.api.quiz import router as quiz_router
from app.api.math import router as math_router
from app.api.progress import router as progress_router

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

def seed_demo_data():
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "student@smartway.ai").first()
        if not demo_user:
            demo_user = User(
                email="student@smartway.ai",
                full_name="Aarav Sharma",
                hashed_password=hash_password("Password@123"),
                role="student",
                language_pref="hinglish",
                theme_pref="dark"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            profile = UserProfile(
                user_id=demo_user.id,
                roll_number="2026/CS/1042",
                father_name="Rajesh Sharma",
                mother_name="Sunita Sharma",
                dob="2005-08-15",
                gender="Male",
                category="OBC",
                village="Rampur",
                district="Varanasi",
                state="Uttar Pradesh",
                pin_code="221001",
                college="National Institute of Technology",
                branch="Computer Science & Engineering",
                section="B",
                academic_year="2025-2026",
                phone_number="+91 98765 43210",
                annual_income="180000",
                aadhar_last4="5432",
                bank_account="918237461928",
                ifsc_code="SBIN0001234"
            )
            db.add(profile)
            db.commit()
    finally:
        db.close()

seed_demo_data()

app = FastAPI(
    title=settings.APP_NAME,
    description="Complete AI Student Platform: AI Teacher, Smart Auto Form Filler, Smart Document Processor, Auto Quiz, Equation Grapher",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(teacher_router, prefix="/api")
app.include_router(forms_router, prefix="/api")
app.include_router(docs_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(math_router, prefix="/api")
app.include_router(progress_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.APP_NAME})

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "database": "connected",
        "gemini_model": settings.GEMINI_MODEL,
        "ai_available": bool(settings.GEMINI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
