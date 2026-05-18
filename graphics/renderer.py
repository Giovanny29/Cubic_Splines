import matplotlib.pyplot as plt


def render_spline(
    points,
    segments,
    title="Natural Cubic Spline"
):

    fig, ax = plt.subplots()

    # =====================================================
    # PONTOS ORIGINAIS
    # =====================================================

    x_points = [p.x for p in points]
    y_points = [p.y for p in points]

    ax.scatter(
        x_points,
        y_points,
        label="Interpolation Points"
    )

    # =====================================================
    # SPLINE
    # =====================================================

    for segment in segments:

        xs = []
        ys = []

        step = (
            segment.x1 - segment.x0
        ) / 200

        x = segment.x0

        while x <= segment.x1:

            y = segment.evaluate(x)

            xs.append(x)
            ys.append(y)

            x += step

        ax.plot(xs, ys)

    # =====================================================
    # VISUAL
    # =====================================================

    ax.set_title(title)

    ax.grid(True)

    ax.legend()

    plt.show()