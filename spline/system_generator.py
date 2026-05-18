from models.point import Point


# =====================================================
# VALIDAÇÃO
# =====================================================

def validate_points(points):

    if len(points) < 3:
        raise ValueError("At least 3 points required for cubic spline")

    for i in range(len(points) - 1):
        if points[i].x >= points[i + 1].x:
            raise ValueError("Points must be strictly sorted by x")


# =====================================================
# h_i = x_{i+1} - x_i
# =====================================================

def compute_h(points):

    h = []

    for i in range(len(points) - 1):

        hi = points[i + 1].x - points[i].x

        if hi == 0:
            raise ValueError("Invalid spline: duplicate x values")

        h.append(hi)

    return h


# =====================================================
# SISTEMA DO SPLINE NATURAL (TRIDIAGONAL)
# =====================================================

def generate_natural_spline_system(points):

    validate_points(points)

    n = len(points) - 1
    h = compute_h(points)

    # =====================================================
    # CASO MÍNIMO (3 pontos → 1 incógnita)
    # =====================================================

    if n == 2:

        A = [[2 * (h[0] + h[1])]]

        d = [
            6 * (
                (points[2].y - points[1].y) / h[1]
                - (points[1].y - points[0].y) / h[0]
            )
        ]

        return A, d

    # =====================================================
    # SISTEMA GERAL
    # =====================================================

    size = n - 1

    A = [[0.0 for _ in range(size)] for _ in range(size)]
    d = [0.0 for _ in range(size)]

    # =====================================================
    # MONTAGEM TRIDIAGONAL
    # =====================================================

    for i in range(size):

        k = i + 1

        h_left = h[k - 1]
        h_right = h[k]

        # subdiagonal
        if i > 0:
            A[i][i - 1] = h_left

        # diagonal principal
        A[i][i] = 2 * (h_left + h_right)

        # superdiagonal
        if i < size - 1:
            A[i][i + 1] = h_right

        # vetor independente
        d[i] = 6 * (
            (points[k + 1].y - points[k].y) / h_right
            - (points[k].y - points[k - 1].y) / h_left
        )

    return A, d