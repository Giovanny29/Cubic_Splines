import numpy as np
from spline.system_generator import generate_natural_spline_system
from spline.spline_segment import SplineSegment
from numerical.gauss_seidel import gauss_seidel_finite
from numerical.jacobi import jacobi_finite

def build_natural_spline(points, machine=None, method="gauss"):
    """
    Constrói a Spline Cúbica comparando a aritmética ideal (referência) 
    com a aritmética de máquina finita.
    """
    if points is None or len(points) < 3:
        return {
            "reference": None, "finite": None,
            "segments_reference": [], "segments_finite": []
        }

    # Garante a ordenação dos pontos
    points = sorted(points, key=lambda p: p.x)
    n = len(points)

    # =====================================================
    # GERAÇÃO DO SISTEMA
    # =====================================================
    # Geramos com e sem máquina para uma comparação real
    A_fin, d_fin = generate_natural_spline_system(points, machine=machine)
    A_ref, d_ref = generate_natural_spline_system(points, machine=None)

    # =====================================================
    # SOLUÇÃO DE REFERÊNCIA (Numpy / Ideal)
    # =====================================================
    try:
        m_ref = np.linalg.solve(A_ref, d_ref).tolist()
    except np.linalg.LinAlgError:
        m_ref = [0.0] * (n - 2)

    reference_result = {
        "solution": m_ref,
        "iterations": 1,
        "error": 0.0,
        "method": "numpy"
    }

    # =====================================================
    # SOLUÇÃO MÁQUINA FINITA
    # =====================================================
    if machine is None:
        return {"reference": reference_result, "finite": None, "segments_reference": [], "segments_finite": []}

    solver = jacobi_finite if method == "jacobi" else gauss_seidel_finite
    
    # Resolve usando a aritmética limitada
    result = solver(A_fin, d_fin, machine, max_iter=100, tol=1e-6)
    
    if not result.get("converged", False):
        print(f"[WARN] {method} não convergiu ou estagnou. Status: {result.get('status')}")

    m_fin = [float(v) for v in result["solution"]]

    finite_result = {
        "solution": m_fin,
        "iterations": result.get("iterations", 0),
        "error": float(result.get("error", 0.0)),
        "method": method,
        "converged": result.get("converged", False),
        "status": result.get("status")
    }

    # =====================================================
    # MONTAGEM DOS SEGMENTOS (M0 = Mn = 0 para Natural)
    # =====================================================
    m_ref_full = [0.0] + m_ref + [0.0]
    m_fin_full = [0.0] + m_fin + [0.0]

    segments_reference = []
    segments_finite = []

    for i in range(n - 1):
        # Segmento Ideal
        segments_reference.append(
            SplineSegment(
                x0=points[i].x, x1=points[i+1].x,
                M0=m_ref_full[i], M1=m_ref_full[i+1],
                y0=points[i].y, y1=points[i+1].y,
                machine=None # Aritmética pura
            )
        )

        # Segmento com Erro de Máquina
        segments_finite.append(
            SplineSegment(
                x0=points[i].x, x1=points[i+1].x,
                M0=m_fin_full[i], M1=m_fin_full[i+1],
                y0=points[i].y, y1=points[i+1].y,
                machine=machine # Avaliação também sofre erro
            )
        )

    return {
        "reference": reference_result,
        "finite": finite_result,
        "segments_reference": segments_reference,
        "segments_finite": segments_finite
    }