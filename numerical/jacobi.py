from numerical.norms import infinity_norm


# =========================================================
# JACOBI COM MÁQUINA FINITA (EXPERIMENTAL)
# =========================================================

from numerical.norms import infinity_norm


def jacobi_finite(A, b, machine, x0=None, tol=1e-6, max_iter=100):

    if machine is None:
        raise ValueError("FiniteMachine not provided")

    n = len(A)

    A = machine.matrix(A)
    b = machine.vector(b)

    if x0 is None:
        x = [machine.fl(0) for _ in range(n)]
    else:
        x = machine.vector(x0)

    for iteration in range(max_iter):

        x_new = [machine.fl(0) for _ in range(n)]

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

            x_new[i] = machine.div(numerator, diag)

        diff = [
            machine.sub(x_new[i], x[i])
            for i in range(n)
        ]

        error = infinity_norm(diff, machine)

        x = x_new

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
# JACOBI DE REFERÊNCIA (IDEAL / SEM MÁQUINA FINITA)
# =========================================================

def jacobi_reference(
    A,
    b,
    x0=None,
    tol=1e-10,
    max_iter=100
):
    """
    Jacobi em aritmética ideal (float Python).
    Usado para comparação de erro.
    """

    n = len(A)

    if x0 is None:
        x0 = [0.0 for _ in range(n)]

    x = [float(v) for v in x0]
    b = [float(v) for v in b]

    for iteration in range(max_iter):

        x_new = [0.0 for _ in range(n)]

        for i in range(n):

            sigma = 0.0

            for j in range(n):

                if i != j:
                    sigma += float(A[i][j]) * x[j]

            x_new[i] = (b[i] - sigma) / float(A[i][i])

        # norma infinita (manual para evitar dependência externa)
        error = max(abs(x_new[i] - x[i]) for i in range(n))

        x = x_new

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