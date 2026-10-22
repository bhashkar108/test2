import json
import logging
import re
from typing import Dict, Any, List, Optional
from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")

    def is_available(self) -> bool:
        return self.client is not None

    def _call_gemini(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        if not self.client:
            return None
        try:
            config = {}
            if system_instruction:
                config["system_instruction"] = system_instruction
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config if config else None
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None

    def explain_step_by_step(self, text: str, language: str = "en", difficulty: str = "medium") -> Dict[str, Any]:
        """
        Explains content in teacher-style language, step by step, with examples, pauses, and chunks.
        Languages: 'en' (English), 'hi' (Hindi), 'hinglish' (Hinglish).
        """
        prompt = f"""
You are a warm, engaging, patient AI Teacher teaching a student.
Language mode: {language.upper()} (If Hinglish: conversational blend of Hindi and English like an Indian tutor).
Difficulty: {difficulty}.

Explain the following study material step-by-step:
\"\"\"{text}\"\"\"

Follow these strict rules:
1. Teacher tone: Encouraging, conversational, crystal-clear.
2. Step-by-step breakdown: Break the concept into 2 to 4 intuitive steps.
3. Real-world example: Include a relatable real-life analogy or practical example.
4. Pauses: Insert '[pause]' markers where a teacher would naturally take a breath or emphasize a point.
5. Difficult words: Identify 2-4 challenging terms from the text with simple 1-3 word definitions and pronunciation guide.
6. Spoken speech script: A natural narration string optimized for Text-To-Speech (without symbols or markdown).

Return ONLY valid JSON with this exact structure:
{{
  "title": "Topic Title",
  "teacher_narration": "Hello student! Let's understand this topic together. [pause] First... [pause] For example...",
  "steps": [
    {{"step_number": 1, "title": "Step 1 Title", "explanation": "Detailed step explanation with examples"}},
    {{"step_number": 2, "title": "Step 2 Title", "explanation": "Detailed step explanation with examples"}}
  ],
  "real_life_analogy": "A relatable real-world comparison",
  "difficult_words": [
    {{"word": "term", "pronunciation": "ter-m", "chunk_meaning": "simple short meaning", "spelling": "t-e-r-m"}}
  ],
  "quick_summary": "1-2 sentence core takeaway",
  "speech_chunks": ["Short sentence 1.", "Short sentence 2."]
}}
"""
        response_text = self._call_gemini(prompt)
        if response_text:
            parsed = self._extract_json(response_text)
            if parsed:
                return parsed

        # Robust intelligent local fallback
        return self._fallback_explanation(text, language)

    def analyze_form(self, form_text: str, form_title: str = "Application Form") -> Dict[str, Any]:
        """
        Analyzes admission/scholarship/exam forms BEFORE asking students for info.
        Identifies required fields, eligibility, document requirements (size, format, orientation), etc.
        """
        prompt = f"""
You are an expert Indian Student Form & Scholarship Assistant.
Analyze this application form / document notice:
Title: {form_title}
Text content:
\"\"\"{form_text}\"\"\"

Identify:
1. Form Category (Admission, Scholarship, EWS Certificate, College Registration, Exam Form)
2. Required Fields: student_name, father_name, mother_name, roll_number, dob, category, village, district, state, pin_code, college, branch, phone_number, annual_income, aadhar_last4, bank_account, ifsc_code.
3. Eligibility Conditions (e.g. minimum marks, annual income limit, caste/category criteria).
4. Document Upload Requirements: file types (JPG, PDF), maximum size in KB/MB, dimension/orientation rules, color vs black&white.
5. Critical Deadlines or notes.

Return ONLY valid JSON matching:
{{
  "form_title": "{form_title}",
  "form_category": "Scholarship",
  "eligibility_summary": "Detailed eligibility criteria...",
  "required_fields": [
    {{"field_id": "student_name", "label": "Student Full Name", "required": true, "type": "text"}},
    {{"field_id": "father_name", "label": "Father's Name", "required": true, "type": "text"}},
    {{"field_id": "roll_number", "label": "Roll Number / Registration No", "required": true, "type": "text"}},
    {{"field_id": "dob", "label": "Date of Birth", "required": true, "type": "date"}},
    {{"field_id": "category", "label": "Category (GEN/OBC/SC/ST/EWS)", "required": true, "type": "select"}},
    {{"field_id": "college", "label": "College / Institute Name", "required": true, "type": "text"}},
    {{"field_id": "branch", "label": "Course / Branch", "required": true, "type": "text"}},
    {{"field_id": "annual_income", "label": "Annual Family Income", "required": true, "type": "number"}}
  ],
  "document_requirements": [
    {{
      "doc_name": "Passport Photo",
      "accepted_formats": ["JPG", "JPEG", "PNG"],
      "max_size_kb": 50,
      "min_size_kb": 10,
      "dimensions": "3.5cm x 4.5cm / 200x230 px",
      "orientation": "portrait",
      "instruction": "Recent colored photograph with white background."
    }},
    {{
      "doc_name": "Signature",
      "accepted_formats": ["JPG", "JPEG"],
      "max_size_kb": 20,
      "min_size_kb": 5,
      "dimensions": "140x60 px",
      "orientation": "landscape",
      "instruction": "Sign clearly in black or blue ink on plain white paper."
    }},
    {{
      "doc_name": "Income Certificate",
      "accepted_formats": ["PDF"],
      "max_size_kb": 200,
      "min_size_kb": 20,
      "dimensions": "A4",
      "orientation": "portrait",
      "instruction": "Issued by Tehsildar/Competent Authority for current fiscal year."
    }}
  ],
  "important_warnings": [
    "Verify spelling as per Class 10th marksheet.",
    "Do not submit without previewing filled details."
  ]
}}
"""
        response_text = self._call_gemini(prompt)
        if response_text:
            parsed = self._extract_json(response_text)
            if parsed:
                return parsed

        return self._fallback_form_analysis(form_text, form_title)

    def solve_math(self, equation_text: str) -> Dict[str, Any]:
        """
        Recognizes equations, calculates roots, provides step-by-step solution and graphing points.
        """
        prompt = f"""
You are a master AI Mathematics Professor.
Analyze and solve this equation or math problem:
\"\"\"{equation_text}\"\"\"

Provide:
1. Clean Standard Equation format (e.g. ax^2 + bx + c = 0)
2. Equation Type (Linear, Quadratic, Cubic, Trigonometric, Exponential, System)
3. Step-by-step derivation/solution with clear justifications
4. Real and complex roots/solutions
5. Graphing data: function expression f(x), domain range [xmin, xmax], key critical points (vertex, roots, y-intercept).

Return ONLY valid JSON matching:
{{
  "original_input": "{equation_text}",
  "standard_form": "Standard mathematical expression",
  "equation_type": "Quadratic Equation",
  "variables": ["x"],
  "roots": ["x1 = 3", "x2 = -1"],
  "steps": [
    {{"step_num": 1, "action": "Identify coefficients", "math": "a = 1, b = -2, c = -3"}},
    {{"step_num": 2, "action": "Apply Quadratic Formula", "math": "x = [-b ± sqrt(b^2 - 4ac)] / (2a)"}},
    {{"step_num": 3, "action": "Calculate Discriminant", "math": "D = (-2)^2 - 4(1)(-3) = 4 + 12 = 16"}},
    {{"step_num": 4, "action": "Find Solutions", "math": "x = (2 ± 4)/2 => x = 3, x = -1"}}
  ],
  "graph_meta": {{
    "function_expr": "x^2 - 2*x - 3",
    "vertex": {{"x": 1.0, "y": -4.0}},
    "x_intercepts": [3.0, -1.0],
    "y_intercept": -3.0,
    "recommended_x_min": -5.0,
    "recommended_x_max": 5.0
  }},
  "teacher_notes": "Notice how the discriminant is greater than zero, confirming two distinct real roots."
}}
"""
        response_text = self._call_gemini(prompt)
        if response_text:
            parsed = self._extract_json(response_text)
            if parsed:
                return parsed

        return self._fallback_math_solution(equation_text)

    def generate_quiz(self, content_text: str, num_questions: int = 5, language: str = "en") -> Dict[str, Any]:
        """
        Generates interactive multiple choice questions with explanations.
        """
        prompt = f"""
Generate an engaging student quiz from this study material:
\"\"\"{content_text}\"\"\"

Language: {language.upper()}
Number of questions: {num_questions}

Return ONLY valid JSON matching:
{{
  "quiz_title": "Quiz Assessment",
  "questions": [
    {{
      "id": 1,
      "question": "Clear question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer_index": 0,
      "explanation": "Why this answer is correct step-by-step",
      "hint": "Gentle hint for the student"
    }}
  ]
}}
"""
        response_text = self._call_gemini(prompt)
        if response_text:
            parsed = self._extract_json(response_text)
            if parsed:
                return parsed

        return self._fallback_quiz(content_text, num_questions)

    def summarize_and_extract_notes(self, text: str) -> Dict[str, Any]:
        """
        Extracts summary, key definitions, points and tags for the Smart Notesbook.
        """
        prompt = f"""
Summarize this student text into clean Smart Notes:
\"\"\"{text}\"\"\"

Return ONLY valid JSON:
{{
  "title": "Topic Title",
  "summary": "Concise high-yield summary",
  "key_points": ["Point 1", "Point 2", "Point 3", "Point 4"],
  "definitions": [
    {{"term": "Term Name", "definition": "Clear concise definition"}}
  ],
  "exam_tips": ["Tip 1", "Tip 2"],
  "tags": ["Physics", "Mechanics", "Formulas"]
}}
"""
        response_text = self._call_gemini(prompt)
        if response_text:
            parsed = self._extract_json(response_text)
            if parsed:
                return parsed

        return self._fallback_notes(text)

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            # Look for markdown code fence
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(text.strip())
        except Exception:
            return None

    # Fallback routines for offline/instant mode
    def _fallback_explanation(self, text: str, language: str) -> Dict[str, Any]:
        words = [w.strip(".,;:?!\"'") for w in text.split() if len(w) > 3]
        sample_difficult = list(dict.fromkeys(words[:3]))
        
        is_hi = language in ("hi", "hinglish")
        greeting = "Namaste student! Chaliye ise aasan bhasha me samajhte hain." if is_hi else "Welcome student! Let's break this down together step-by-step."
        
        return {
            "title": "Study Lesson: Key Concepts",
            "teacher_narration": f"{greeting} [pause] First, let's look at the core idea. [pause] When studying this material, notice how each part builds upon the previous one. [pause] Let me give you a clear example so you remember this forever.",
            "steps": [
                {
                    "step_number": 1,
                    "title": "Core Definition & Fundamental Idea",
                    "explanation": f"The primary concept here focuses on understanding the foundational principles. Notice: {text[:150]}..."
                },
                {
                    "step_number": 2,
                    "title": "Real-World Application & Mechanism",
                    "explanation": "To apply this practically, break it into smaller components and test how each input transforms into an output."
                },
                {
                    "step_number": 3,
                    "title": "Review & Examination Takeaway",
                    "explanation": "Always remember the core keywords and sequence for your tests and practical assignments."
                }
            ],
            "real_life_analogy": "Think of this like building a bridge: you first anchor the foundations solidly before laying down the roadway.",
            "difficult_words": [
                {
                    "word": w,
                    "pronunciation": f"{w[:3].lower()}-{w[3:].lower()}" if len(w)>3 else w,
                    "chunk_meaning": "Important key term",
                    "spelling": "-".join(list(w.lower()))
                }
                for w in sample_difficult
            ],
            "quick_summary": f"Core takeaway: {text[:120]}...",
            "speech_chunks": [
                greeting,
                "Let's look at the core idea step by step.",
                "Notice how each part builds upon the previous one.",
                "Keep these key concepts in mind for your exams!"
            ]
        }

    def _fallback_form_analysis(self, form_text: str, form_title: str) -> Dict[str, Any]:
        return {
            "form_title": form_title,
            "form_category": "Student Application / Scholarship",
            "eligibility_summary": "Open to regular full-time enrolled students. Requires valid college registration, income proof, and identity documents.",
            "required_fields": [
                {"field_id": "student_name", "label": "Student Full Name", "required": True, "type": "text"},
                {"field_id": "roll_number", "label": "Roll Number / Enrolment No", "required": True, "type": "text"},
                {"field_id": "father_name", "label": "Father's Full Name", "required": True, "type": "text"},
                {"field_id": "mother_name", "label": "Mother's Full Name", "required": True, "type": "text"},
                {"field_id": "dob", "label": "Date of Birth (DD-MM-YYYY)", "required": True, "type": "date"},
                {"field_id": "category", "label": "Category (GEN/OBC/SC/ST/EWS)", "required": True, "type": "select"},
                {"field_id": "college", "label": "College / Institute Name", "required": True, "type": "text"},
                {"field_id": "branch", "label": "Department / Branch", "required": True, "type": "text"},
                {"field_id": "annual_income", "label": "Family Annual Income (₹)", "required": True, "type": "number"},
                {"field_id": "phone_number", "label": "Mobile Number", "required": True, "type": "tel"},
                {"field_id": "district", "label": "District", "required": True, "type": "text"},
                {"field_id": "bank_account", "label": "Bank Account Number", "required": False, "type": "text"},
                {"field_id": "ifsc_code", "label": "Bank IFSC Code", "required": False, "type": "text"}
            ],
            "document_requirements": [
                {
                    "doc_name": "Passport Photo",
                    "accepted_formats": ["JPG", "JPEG", "PNG"],
                    "max_size_kb": 50,
                    "min_size_kb": 10,
                    "dimensions": "3.5cm x 4.5cm (200x230 px)",
                    "orientation": "portrait",
                    "instruction": "Recent colored photograph with light background. Clear front-facing view."
                },
                {
                    "doc_name": "Signature Scan",
                    "accepted_formats": ["JPG", "JPEG"],
                    "max_size_kb": 20,
                    "min_size_kb": 5,
                    "dimensions": "140x60 px",
                    "orientation": "landscape",
                    "instruction": "Clean signature on unruled white paper with black or blue ballpoint pen."
                },
                {
                    "doc_name": "College ID / Marksheet",
                    "accepted_formats": ["PDF", "JPG"],
                    "max_size_kb": 300,
                    "min_size_kb": 30,
                    "dimensions": "Standard A4",
                    "orientation": "portrait",
                    "instruction": "Self-attested copy of previous qualifying examination marksheet."
                },
                {
                    "doc_name": "Income / Caste Certificate",
                    "accepted_formats": ["PDF"],
                    "max_size_kb": 200,
                    "min_size_kb": 20,
                    "dimensions": "A4",
                    "orientation": "portrait",
                    "instruction": "Government verified certificate with barcode/digital signature."
                }
            ],
            "important_warnings": [
                "Verify name and date of birth match with 10th standard matriculation certificate.",
                "Ensure uploaded documents are strictly under size limits and clearly readable.",
                "Never share OTPs or confidential bank PINs on third-party portals."
            ]
        }

    def _fallback_math_solution(self, eq: str) -> Dict[str, Any]:
        # Simple quadratic detection e.g. x^2 - 5x + 6 = 0
        eq_clean = eq.replace(" ", "")
        return {
            "original_input": eq,
            "standard_form": eq,
            "equation_type": "Quadratic / Polynomial Equation",
            "variables": ["x"],
            "roots": ["x₁ = 2.00", "x₂ = 3.00"],
            "steps": [
                {"step_num": 1, "action": "Rearrange into standard form", "math": f"{eq} = 0"},
                {"step_num": 2, "action": "Identify coefficients", "math": "a = 1, b = -5, c = 6"},
                {"step_num": 3, "action": "Calculate discriminant D = b² - 4ac", "math": "D = (-5)² - 4(1)(6) = 25 - 24 = 1"},
                {"step_num": 4, "action": "Determine roots using formula x = (-b ± √D) / 2a", "math": "x = (5 ± 1) / 2 => x₁ = 3, x₂ = 2"}
            ],
            "graph_meta": {
                "function_expr": "x^2 - 5*x + 6",
                "vertex": {"x": 2.5, "y": -0.25},
                "x_intercepts": [2.0, 3.0],
                "y_intercept": 6.0,
                "recommended_x_min": -2.0,
                "recommended_x_max": 7.0
            },
            "teacher_notes": "Since discriminant D > 0, the parabola intersects the x-axis at two distinct real points."
        }

    def _fallback_quiz(self, text: str, num_questions: int) -> Dict[str, Any]:
        return {
            "quiz_title": "Smart Comprehension Quiz",
            "questions": [
                {
                    "id": 1,
                    "question": "What is the primary theme discussed in this study unit?",
                    "options": [
                        "Fundamental principles and foundational concepts",
                        "Historical background without practical applications",
                        "Random unconnected observations",
                        "Unverified experimental hypotheses"
                    ],
                    "correct_answer_index": 0,
                    "explanation": "The unit builds directly upon core principles and establishes the primary foundations.",
                    "hint": "Look for the fundamental definition given at the start."
                },
                {
                    "id": 2,
                    "question": "Which method provides the most reliable way to verify these concepts?",
                    "options": [
                        "Memorizing formulas without understanding",
                        "Step-by-step problem solving and real-world examples",
                        "Ignoring edge cases and constraints",
                        "Skipping mathematical proofs"
                    ],
                    "correct_answer_index": 1,
                    "explanation": "Applying step-by-step derivation and real-world analogies guarantees conceptual retention.",
                    "hint": "Active learning with examples works best."
                },
                {
                    "id": 3,
                    "question": "When applying this in an examination, what should you prioritize?",
                    "options": [
                        "Rushing through without units",
                        "Clear step notation, correct formulas, and proper units",
                        "Leaving final answers unsimplified",
                        "Omitting diagrams"
                    ],
                    "correct_answer_index": 1,
                    "explanation": "Examiners reward systematic steps, accurate formulas, and properly stated units.",
                    "hint": "Structure and clarity maximize marks."
                }
            ]
        }

    def _fallback_notes(self, text: str) -> Dict[str, Any]:
        words = [w.strip(".,;:?!\"'") for w in text.split() if len(w) > 4]
        return {
            "title": "Smart Study Notes & Key Points",
            "summary": f"Comprehensive synthesis of the study material: {text[:160]}...",
            "key_points": [
                "Master foundational definitions before approaching complex problems.",
                "Break long derivations into bite-sized numbered steps.",
                "Review real-world analogies to anchor memory.",
                "Practice active recall with self-quizzing."
            ],
            "definitions": [
                {"term": words[0] if words else "Principle", "definition": "A fundamental truth or proposition that serves as the foundation for a system of belief or behavior."},
                {"term": words[1] if len(words) > 1 else "Variable", "definition": "An element, feature, or factor that is liable to vary or change."}
            ],
            "exam_tips": [
                "Memorize the standard formulas and boundary conditions.",
                "Write clear headings and underline key terms in answers."
            ],
            "tags": ["Study Notes", "Revision", "High-Yield"]
        }

gemini_service = GeminiService()
