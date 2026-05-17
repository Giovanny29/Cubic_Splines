from models.point import Point


def validate_points(points):

    if len(points) < 3:
        raise ValueError(
            "At least 3 points are required"
        )

    xs = [p.x for p in points]

    if len(xs) != len(set(xs)):
        raise ValueError(
            "Repeated x coordinates are not allowed"
        )

    for i in range(len(xs) - 1):

        if xs[i] >= xs[i + 1]:
            raise ValueError(
                "Points must be sorted by x"
            )


def compute_h(points):

    h = []

    for i in range(len(points) - 1):

        h.append(
            points[i + 1].x - points[i].x
        )

    return h


def generate_natural_spline_system(points):

    validate_points(points)

    n = len(points) - 1

    h = compute_h(points)

    # =====================================================
    # CASO:
    # apenas 3 pontos
    # sistema 1x1
    # =====================================================

    if n == 2:

        A = [[
            2 * (h[0] + h[1])
        ]]

        d = [[
            6 * (
                (points[2].y - points[1].y) / h[1]
                -
                (points[1].y - points[0].y) / h[0]
            )
        ]]

        return A, d

    # =====================================================
    # SISTEMA GERAL
    # =====================================================

    size = n - 1

    A = [
        [0 for _ in range(size)]
        for _ in range(size)
    ]

    d = [0 for _ in range(size)]

    # =====================================================
    # MONTA MATRIZ
    # =====================================================

    for i in range(1, n):

        row = i - 1

        # diagonal inferior
        if row > 0:

            A[row][row - 1] = h[i - 1]

        # diagonal principal
        A[row][row] = 2 * (
            h[i - 1] + h[i]
        )

        # diagonal superior
        if row < size - 1:

            A[row][row + 1] = h[i]

        # vetor independente

        term1 = (
            (points[i + 1].y - points[i].y)
            / h[i]
        )

        term2 = (
            (points[i].y - points[i - 1].y)
            / h[i - 1]
        )

        d[row] = 6 * (term1 - term2)

    return A, d