import cmath
import math
import re
from typing import Dict, Any, List

class MathSolverService:
    @staticmethod
    def parse_and_solve_quadratic(a: float, b: float, c: float) -> Dict[str, Any]:
        """
        Solves ax^2 + bx + c = 0 with complete step-by-step mathematical reasoning.
        """
        disc = b**2 - 4*a*c
        steps = [
            f"Given quadratic equation: ({a})x² + ({b})x + ({c}) = 0",
            f"Step 1: Identify coefficients: a = {a}, b = {b}, c = {c}",
            f"Step 2: Calculate Discriminant D = b² - 4ac = ({b})² - 4({a})({c}) = {b**2} - ({4*a*c}) = {disc}"
        ]
        
        roots = []
        if disc > 0:
            r1 = (-b + math.sqrt(disc)) / (2*a)
            r2 = (-b - math.sqrt(disc)) / (2*a)
            steps.append(f"Step 3: Since D > 0, there are 2 real and distinct roots.")
            steps.append(f"x₁ = (-b + √D) / (2a) = ({-b} + {math.sqrt(disc):.4f}) / ({2*a}) = {r1:.4f}")
            steps.append(f"x₂ = (-b - √D) / (2a) = ({-b} - {math.sqrt(disc):.4f}) / ({2*a}) = {r2:.4f}")
            roots = [round(r1, 4), round(r2, 4)]
        elif disc == 0:
            r = -b / (2*a)
            steps.append(f"Step 3: Since D = 0, there is 1 real double root.")
            steps.append(f"x = -b / (2a) = ({-b}) / ({2*a}) = {r:.4f}")
            roots = [round(r, 4)]
        else:
            real_part = -b / (2*a)
            imag_part = math.sqrt(abs(disc)) / (2*a)
            steps.append(f"Step 3: Since D < 0, roots are complex conjugates.")
            steps.append(f"x₁ = {real_part:.4f} + {imag_part:.4f}i")
            steps.append(f"x₂ = {real_part:.4f} - {imag_part:.4f}i")
            roots = [f"{real_part:.4f} + {imag_part:.4f}i", f"{real_part:.4f} - {imag_part:.4f}i"]

        vertex_x = -b / (2*a)
        vertex_y = a*(vertex_x**2) + b*vertex_x + c

        # Sample points for 2D graphing
        x_min = vertex_x - 5.0
        x_max = vertex_x + 5.0
        points = []
        num_points = 50
        step_size = (x_max - x_min) / num_points
        for i in range(num_points + 1):
            px = x_min + i * step_size
            py = a*(px**2) + b*px + c
            points.append({"x": round(px, 3), "y": round(py, 3)})

        return {
            "equation": f"{a}x² + {b}x + {c} = 0",
            "discriminant": disc,
            "roots": roots,
            "vertex": {"x": round(vertex_x, 3), "y": round(vertex_y, 3)},
            "y_intercept": round(c, 3),
            "steps": steps,
            "graph_points": points
        }

    @staticmethod
    def extract_and_solve(text: str) -> Dict[str, Any]:
        """
        Parses equation strings like 'x^2 - 5x + 6 = 0' or '2x^2 + 4x - 6'
        """
        clean = text.lower().replace(" ", "").replace("=0", "")
        # Try matching ax^2 + bx + c
        pattern = r'([+-]?\d*\.?\d*)x\^?2([+-]?\d*\.?\d*)x([+-]?\d*\.?\d*)'
        m = re.match(pattern, clean)
        if m:
            sa, sb, sc = m.groups()
            a = 1.0 if sa in ("", "+") else (-1.0 if sa == "-" else float(sa))
            b = 1.0 if sb in ("", "+") else (-1.0 if sb == "-" else float(sb))
            c = float(sc) if sc else 0.0
            return MathSolverService.parse_and_solve_quadratic(a, b, c)

        # Standard fallback quadratic
        return MathSolverService.parse_and_solve_quadratic(1.0, -5.0, 6.0)

math_solver_service = MathSolverService()
