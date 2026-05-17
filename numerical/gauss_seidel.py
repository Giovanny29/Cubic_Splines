from numerical.norms import infinity_norm


def gauss_seidel(
    A,
    b,
    machine,
    x0=None,
    tol=1e-6,
    max_iter=100
):

    n = len(A)

    if x0 is None:
        x0 = [0] * n

    x = machine.vector(x0)

    error = machine.fl(0)

    for iteration in range(max_iter):

        try:

            x_old = x.copy()

            # =====================================================
            # ITERAÇÃO GAUSS-SEIDEL
            # =====================================================

            for i in range(n):

                sigma = machine.fl(0)

                for j in range(n):

                    if i != j:

                        product = machine.mul(
                            A[i][j],
                            x[j]
                        )

                        sigma = machine.add(
                            sigma,
                            product
                        )

                numerator = machine.sub(
                    b[i],
                    sigma
                )

                x[i] = machine.div(
                    numerator,
                    A[i][i]
                )

            # =====================================================
            # ERRO
            # =====================================================

            diff = []

            for i in range(n):

                diff.append(
                    machine.sub(
                        x[i],
                        x_old[i]
                    )
                )

            error = infinity_norm(
                diff,
                machine
            )

            # =====================================================
            # CONVERGIU
            # =====================================================

            if error < tol:

                return {
                    "solution": x,
                    "iterations": iteration + 1,
                    "converged": True,
                    "error": error
                }

        # =========================================================
        # OVERFLOW / ERROS NUMÉRICOS
        # =========================================================

        except Exception as e:

            return {
                "solution": x,
                "iterations": iteration + 1,
                "converged": False,
                "error": str(e)
            }

    # =============================================================
    # NÃO CONVERGIU
    # =============================================================

    return {
        "solution": x,
        "iterations": max_iter,
        "converged": False,
        "error": error
    }