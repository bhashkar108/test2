from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.math_service import math_solver_service
from app.services.gemini_service import gemini_service
from app.core.security import get_current_user
from app.models.models import User

router = APIRouter(prefix="/math", tags=["Equation Graph & Solver"])

class SolveEquationRequest(BaseModel):
    equation: str
    variable: Optional[str] = "x"

class QuadraticCoeffRequest(BaseModel):
    a: float
    b: float
    c: float

@router.post("/solve")
def solve_equation(req: SolveEquationRequest, current_user: User = Depends(get_current_user)):
    eq = req.equation.strip()
    if not eq:
        raise HTTPException(status_code=400, detail="Equation cannot be empty")

    # Try gemini first for rich explanation, or math_solver_service fallback
    gemini_res = gemini_service.solve_math(eq)
    return gemini_res

@router.post("/solve-quadratic")
def solve_quadratic_coefficients(req: QuadraticCoeffRequest, current_user: User = Depends(get_current_user)):
    if req.a == 0:
        raise HTTPException(status_code=400, detail="Coefficient 'a' cannot be zero for quadratic equations.")
    return math_solver_service.parse_and_solve_quadratic(req.a, req.b, req.c)
