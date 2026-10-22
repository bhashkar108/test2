# TECH AI | Smart Way
### Complete AI Student Platform: Master Implementation

**TECH AI | Smart Way** is a production-grade, full-stack AI-powered learning and student utility platform engineered with FastAPI, Python, Google Gemini (`google-genai`), MySQL 8.x / SQLite, and a mobile-first dashboard.

---

## 🌟 Key Features

### 1. AI Teacher & Smart Notesbook
- **Interactive Explanations:** Upload PDFs or paste lecture notes. Explains concepts step-by-step with real-world analogies and natural pauses (`[pause]`).
- **Karaoke Word & Sentence Tracking:** Word-by-word and sentence-by-sentence highlighting synchronized with Web Speech API audio, auto-scrolling as the teacher explains.
- **Dynamic Audio Orb & Waveform:** Visual glowing gradient orb and responsive wave visualizer that pulses only while speech is active.
- **Speech Controls:** Adjustable speech rate (0.75x, 1.0x, 1.25x, 1.5x), sentence repeat, pause, resume, stop, and previous/next sentence buttons.
- **Difficult Word Assistant:** Automatically extracts difficult vocabulary, offering 1–3 word breakdowns, phonetics, spelling, and audio pronunciation.
- **Voice Commands:** Hands-free voice recognition supporting commands: `"stop"`, `"ruko"`, `"repeat"`, `"aage bolo"`, `"continue"`, and `"done"`.
- **Smart Notesbook:** Automatic extraction of high-yield exam summaries, key definitions, and database persistence.

### 2. Smart Auto Form Filler
- **Pre-Analysis Engine:** Analyzes admission, scholarship, and EWS circulars **BEFORE** prompting the student for data.
- **Constraint Detection:** Discovers required fields, eligibility criteria, document specs (file size limits, portrait/landscape orientation, accepted formats).
- **Profile Cross-Matching:** Cross-checks requirements against the student's saved master profile.
- **Blue Checkmark Checklist:** Visual checklist prominently featured on mobile showing satisfied requirements with blue checkmarks and prompting only for missing details.
- **Live Form Preview:** Editable summary with instant PDF/Print export.
- **Document Prepper:** Quick rotation, compression to under 50KB, and image-to-PDF conversion.

### 3. Smart Document Processor
- **Document Capture & Upload:** Supports PDF, JPEG, PNG, WEBP, and real-time device camera capture.
- **Client & Server Operations:** 90° rotation, high-contrast B&W thresholding, quality compression slider, and PDF export while preserving original files.
- **Mathematical Document Support:** Extracts formulas, identifies equation degree, solves roots, and provides step-by-step derivations.

### 4. Auto Quiz Generator
- **AI-Powered Practice:** Generates 5 conceptual multiple-choice questions from any study material or textbook topic.
- **Interactive Testing:** Immediate explanation upon answer selection, helpful hints, and score tracking with database history.

### 5. 2D Equation Graph & Math Studio
- **Coordinate Grapher:** Interactive canvas powered by `math.js`.
- **Real-Time Tracing:** Mouse hover displays real-time `(x, y)` coordinates.
- **Quadratic Equation Calculator:** Solves $ax^2 + bx + c = 0$, calculates roots, vertex coordinates, and discriminant $D = b^2 - 4ac$, automatically plotting the resulting parabola.

### 6. Progress & Master Student Profile
- **Analytics Dashboard:** Tracks study streak days, total hours learned, and quiz accuracy with interactive Chart.js bar graphs.
- **Master Student Profile:** Centralized store for roll number, parent names, category, village, district, college, branch, income, bank details, and Aadhaar info.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **AI Integration:** Google Gemini API (`google-genai`), configurable via `.env`
- **Database:** MySQL 8.x with SQLAlchemy and PyMySQL (with automatic fallback to SQLite for zero-setup execution)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (ES6+), Lucide Icons, Math.js, Chart.js
- **Audio & Speech:** Web Speech Synthesis (TTS) & Web Speech Recognition APIs

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or later
- (Optional) MySQL 8.x database server

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
To use Google Gemini, set your API key in `.env`:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
GEMINI_MODEL="gemini-2.5-flash"
```
*(Note: If no API key is provided, the application runs in local intelligence fallback mode with complete step-by-step teacher explanations, quizzes, and math solutions.)*

### 3. Run the Server
From the project folder:
```bash
python run.py
```
Open your browser and navigate to:
**http://127.0.0.1:8000**

### 4. Instant Demo Account
For instant 1-click evaluation without registration:
- **Email:** `student@smartway.ai`
- **Password:** `Password@123`
*(Or click the **"Sign In as Demo Student (Aarav Sharma)"** button on the sign-in modal.)*

---

## 🗄️ MySQL 8.x Database Setup (Optional)
To use MySQL 8.x instead of SQLite:
1. Create the database:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
2. Update `.env`:
   ```env
   DATABASE_URL="mysql+pymysql://root:yourpassword@localhost:3306/tech_ai_db"
   ```

---

## 📂 Project Structure
```
tech-ai-smart-way/
├── app/
│   ├── api/
│   │   ├── auth.py          # Authentication & Profile routes
│   │   ├── teacher.py       # AI Teacher & Notesbook routes
│   │   ├── forms.py         # Auto Form Filler routes
│   │   ├── docs.py          # Document Processor routes
│   │   ├── quiz.py          # Auto Quiz routes
│   │   ├── math.py          # Math solver & Quadratic routes
│   │   └── progress.py      # Student Analytics routes
│   ├── core/
│   │   ├── config.py        # Environment & App settings
│   │   ├── database.py      # SQLAlchemy engine & fallback
│   │   └── security.py      # Password hashing & JWT tokens
│   ├── models/
│   │   └── models.py        # SQLAlchemy ORM models
│   ├── services/
│   │   ├── gemini_service.py# Google Gemini API & Teacher prompts
│   │   ├── doc_service.py   # PDF text extraction (pypdf)
│   │   └── math_service.py  # Quadratic & root solvers
│   └── main.py              # FastAPI app & routing
├── database/
│   └── schema.sql           # MySQL 8.x initialization script
├── static/
│   ├── css/
│   │   └── style.css        # Responsive dark/light theme tokens & styles
│   └── js/
│       ├── app.js           # App state & auth wrapper
│       └── modules/
│           ├── teacher.js   # Voice synthesis, karaoke, voice cmds
│           ├── form_filler.js# Requirements engine & live preview
│           ├── doc_processor.js# Camera capture, canvas tools
│           ├── quiz.js      # Interactive MCQs & timer
│           ├── grapher.js   # 2D Canvas equation plotter
│           └── profile.js   # Master profile & Chart.js analytics
├── templates/
│   └── index.html           # Main single-page dashboard
├── uploads/                 # Storage for uploaded documents
├── .env.example             # Template environment variables
├── requirements.txt         # Dependencies
├── run.py                   # One-click startup script
└── README.md                # Documentation
```
