from numerical.norms import infinity_norm


# =========================================================
# GAUSS-SEIDEL FINITO (CORRIGIDO)
# =========================================================

from numerical.norms import infinity_norm


def gauss_seidel_finite(
    A,
    b,
    machine,
    x0=None,
    tol=1e-6,
    max_iter=100
):

    if machine is None:
        raise ValueError("Machine cannot be None in Gauss-Seidel")

    n = len(A)

    # =====================================================
    # CONSISTÊNCIA TOTAL NA MÁQUINA
    # =====================================================

    A = machine.matrix(A)
    b = machine.vector(b)

    if x0 is None:
        x = [machine.fl(0) for _ in range(n)]
    else:
        x = machine.vector(x0)

    for iteration in range(max_iter):

        x_old = x.copy()

        for i in range(n):

            sigma = machine.fl(0)

            for j in range(n):

                if i != j:
                    sigma = machine.add(
                        sigma,
                        machine.mul(A[i][j], x[j])
                    )

            numerator = machine.sub(b[i], sigma)

            diag = A[i][i]

            if diag == 0:
                raise ZeroDivisionError(f"Zero diagonal at row {i}")

            x[i] = machine.div(numerator, diag)

        # =================================================
        # ERRO (CONSISTENTE COM MACHINE)
        # =================================================

        diff = [
            machine.sub(x[i], x_old[i])
            for i in range(n)
        ]

        error = infinity_norm(diff, machine)

        if error < tol:
            return {
                "solution": x,
                "iterations": iteration + 1,
                "converged": True,
                "error": error
            }

    return {
        "solution": x,
        "iterations": max_iter,
        "converged": False,
        "error": error
    }


# =========================================================
# REFERÊNCIA (FLOAT PURO)
# =========================================================

def gauss_seidel_reference(
    A,
    b,
    x0=None,
    tol=1e-10,
    max_iter=100
):

    n = len(A)

    if x0 is None:
        x = [0.0 for _ in range(n)]
    else:
        x = [float(v) for v in x0]

    A = [[float(v) for v in row] for row in A]
    b = [float(v) for v in b]

    for iteration in range(max_iter):

        x_old = x.copy()

        for i in range(n):

            sigma = 0.0

            for j in range(n):

                if i != j:
                    sigma += A[i][j] * x[j]

            x[i] = (b[i] - sigma) / A[i][i]

        error = max(abs(x[i] - x_old[i]) for i in range(n))

        if error < tol:
            return {
                "solution": x,
                "iterations": iteration + 1,
                "converged": True,
                "error": error
            }

    return {
        "solution": x,
        "iterations": max_iter,
        "converged": False,
        "error": error
    }


# compatibilidade
gauss_seidel = gauss_seidel_finite