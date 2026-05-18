from models.point import Point

from numerical.machine import (
    FiniteMachine,
    RoundingMode
)

from spline.spline_builder import (
    build_natural_spline
)

from graphics.renderer import (
    render_spline
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
# RENDER
# =========================================================

render_spline(
    points,
    segments
)