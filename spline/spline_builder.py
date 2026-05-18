import numpy as np

from spline.system_generator import generate_natural_spline_system
from spline.spline_segment import SplineSegment

from numerical.gauss_seidel import gauss_seidel_finite
from numerical.jacobi import jacobi_finite


# =========================================================
# SPLINE BUILDER (COMPARAÇÃO EXPLÍCITA)
# =========================================================

def build_natural_spline(
    points,
    machine=None,
    method="gauss"  # "gauss" | "jacobi"
):
    """
    Retorna:
        - reference (numpy ideal)
        - finite (máquina finita)
        - segments_reference
        - segments_finite
    """

    if points is None or len(points) < 2:
        return {
            "reference": None,
            "finite": None,
            "segments_reference": [],
            "segments_finite": []
        }

    # =====================================================
    # ORDEM (essencial)
    # =====================================================

    points = sorted(points, key=lambda p: p.x)

    # =====================================================
    # SISTEMA LINEAR (Spline natural)
    # =====================================================

    A, d = generate_natural_spline_system(points)

    n = len(points)

    # =====================================================
    # REFERÊNCIA (SÓ REALMENTE INTERNA)
    # =====================================================

    m_ref = np.linalg.solve(A, d)
    m_ref = [float(v) for v in m_ref]

    reference_result = {
        "solution": m_ref,
        "iterations": 1,
        "error": 0.0,
        "method": "numpy"
    }

    # =====================================================
    # MÁQUINA FINITA
    # =====================================================

    if machine is None:
        return {
            "reference": reference_result,
            "finite": None,
            "segments_reference": [],
            "segments_finite": []
        }

    if method == "jacobi":
        result = jacobi_finite(
            A, d,
            machine,
            max_iter=50,
            tol=1e-6
        )
    else:
        result = gauss_seidel_finite(
            A, d,
            machine,
            max_iter=50,
            tol=1e-6
        )

    if not result.get("converged", False):
        print(f"[WARN] {method} não convergiu: {result.get('error')}")

    m_fin = [float(v) for v in result["solution"]]

    finite_result = {
        "solution": m_fin,
        "iterations": result.get("iterations", 0),
        "error": float(result.get("error", 0.0)),
        "method": method,
        "converged": result.get("converged", False)
    }

    # =====================================================
    # SPLINE NATURAL
    # M0 = Mn = 0
    # =====================================================

    m_ref_full = [0.0] + m_ref + [0.0]
    m_fin_full = [0.0] + m_fin + [0.0]

    # segurança estrutural
    if len(m_ref_full) != n or len(m_fin_full) != n:
        print("[WARN] dimensão inconsistente do vetor M")
        return {
            "reference": reference_result,
            "finite": finite_result,
            "segments_reference": [],
            "segments_finite": []
        }

    # =====================================================
    # SEGMENTOS
    # =====================================================

    segments_reference = []
    segments_finite = []

    for i in range(n - 1):

        segments_reference.append(
            SplineSegment(
                x0=points[i].x,
                x1=points[i + 1].x,
                M0=m_ref_full[i],
                M1=m_ref_full[i + 1],
                y0=points[i].y,
                y1=points[i + 1].y
            )
        )

        segments_finite.append(
            SplineSegment(
                x0=points[i].x,
                x1=points[i + 1].x,
                M0=m_fin_full[i],
                M1=m_fin_full[i + 1],
                y0=points[i].y,
                y1=points[i + 1].y
            )
        )

    # =====================================================
    # RETORNO FINAL
    # =====================================================

    return {
        "reference": reference_result,
        "finite": finite_result,
        "segments_reference": segments_reference,
        "segments_finite": segments_finite
    }