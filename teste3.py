from models.point import Point

from numerical.machine import (
    FiniteMachine,
    RoundingMode
)

from spline.spline_builder import (
    build_natural_spline
)

# =========================================================
# MÁQUINA
# =========================================================

machine = FiniteMachine(
    base=10,
    precision=6,
    exponent_min=-10,
    exponent_max=10,
    rounding=RoundingMode.ROUND
)

# =========================================================
# PONTOS
# =========================================================

points = [
    Point(0, 0),
    Point(1, 1),
    Point(2, 0),
    Point(3, 1)
]

# =========================================================
# SPLINE
# =========================================================

segments = build_natural_spline(
    points,
    machine
)

# =========================================================
# TESTES
# =========================================================

print("\nSPLINE SEGMENTS")
print()

for i, segment in enumerate(segments):

    print(f"Segment {i}")

    print(
        f"[{segment.x0}, {segment.x1}]"
    )

    print(
        f"M0 = {segment.M0}"
    )

    print(
        f"M1 = {segment.M1}"
    )

    print()

# =========================================================
# TESTE DE INTERPOLAÇÃO
# =========================================================

print("\nINTERPOLATION TEST")
print()

for segment in segments:

    x0 = segment.x0
    x1 = segment.x1

    y0 = segment.evaluate(x0)
    y1 = segment.evaluate(x1)

    print(f"x = {x0} -> y = {y0}")
    print(f"x = {x1} -> y = {y1}")
    print()

# =========================================================
# AMOSTRAGEM DA CURVA
# =========================================================

print("\nCURVE SAMPLING")
print()

samples = [
    0,
    0.25,
    0.5,
    0.75,
    1,
    1.25,
    1.5,
    1.75,
    2,
    2.25,
    2.5,
    2.75,
    3
]

for x in samples:

    for segment in segments:

        if segment.contains(x):

            y = segment.evaluate(x)

            print(
                f"x = {x:.2f} -> y = {y:.6f}"
            )

            break