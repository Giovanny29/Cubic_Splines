from spline.system_generator import (
    generate_natural_spline_system,
    compute_h
)

from spline.spline_segment import (
    SplineSegment
)

from numerical.gauss_seidel import (
    gauss_seidel
)


def build_natural_spline(
    points,
    machine,
    solver="gauss_seidel"
):

    A, d = generate_natural_spline_system(points)

    # =====================================================
    # RESOLVE SISTEMA
    # =====================================================

    if solver == "gauss_seidel":

        result = gauss_seidel(
            A,
            d,
            machine
        )

    else:
        raise ValueError(
            "Unsupported solver"
        )

    internal_M = result["solution"]

    # =====================================================
    # RECONSTRÓI:
    #
    # M0 = 0
    # Mn = 0
    # =====================================================

    M = [0]

    for value in internal_M:
        M.append(float(value))

    M.append(0)

    h = compute_h(points)

    segments = []

    # =====================================================
    # CONSTRÓI SPLINES
    # =====================================================

    for i in range(len(points) - 1):

        segment = SplineSegment(
            x0=points[i].x,
            x1=points[i + 1].x,
            M0=M[i],
            M1=M[i + 1],
            y0=points[i].y,
            y1=points[i + 1].y,
            h=h[i]
        )

        segments.append(segment)

    return segments