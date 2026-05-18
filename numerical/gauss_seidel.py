"""
Module: gauss_seidel.py
Description: Implementation of the Gauss-Seidel Iterative Method for solving linear systems 
             using both finite machine arithmetic and ideal reference arithmetic.
"""
from decimal import Decimal
from numerical.norms import infinity_norm
from numerical.machine import OverflowMachineError

# =========================================================
# GAUSS-SEIDEL COM MÁQUINA FINITA (EXPERIMENTAL)
# =========================================================

def gauss_seidel_finite(A, b, machine, x0=None, tol=1e-6, max_iter=100):
    """
    Resolve o sistema linear Ax = b pelo método iterativo de Gauss-Seidel
    utilizando estritamente a aritmética limitada da máquina finita.
    Atualiza as componentes do vetor solução imediatamente dentro da mesma iteração.

    Entrada:
        A (list[list]): Matriz de coeficientes do sistema.
        b (list): Vetor de termos independentes.
        machine (FiniteMachine): Instância da máquina virtual para processamento aritmético.
        x0 (list, opcional): Vetor de aproximação inicial. Se None, inicializa com zeros.
        tol (float): Tolerância para o critério de parada baseada na norma do erro absoluto.
        max_iter (int): Número máximo de iterações permitidas.
    Saída:
        dict: Relatório contendo:
            - "solution" (list[Decimal]): O vetor solução aproximado obtido pela máquina.
            - "iterations" (int): O total de iterações executadas.
            - "converged" (bool): True se atingiu a tolerância, False caso contrário.
            - "error" (Decimal): O erro da última iteração calculada.
            - "status" (str): Descrição do estado final da execução.
    """
    if machine is None:
        raise ValueError("FiniteMachine not provided to gauss_seidel_finite.")

    n = len(A)

    # Conversão das estruturas para representação interna da máquina
    A_m = machine.matrix(A)
    b_m = machine.vector(b)

    if x0 is None:
        x = [machine.fl(0) for _ in range(n)]
    else:
        x = machine.vector(x0)

    error = machine.fl(0)

    for iteration in range(max_iter):
        # Guarda o estado anterior para cálculo do critério de parada
        x_old = x.copy()

        try:
            for i in range(n):
                sigma = machine.fl(0)

                for j in range(n):
                    if i != j:
                        # Como alteramos 'x' em tempo real, j < i usa o valor novo (k+1)
                        # e j > i usa o valor antigo (k), respeitando Gauss-Seidel.
                        term = machine.mul(A_m[i][j], x[j])
                        sigma = machine.add(sigma, term)

                numerator = machine.sub(b_m[i], sigma)
                diag = A_m[i][i]

                if diag == 0:
                    raise ZeroDivisionError(f"Zero diagonal element detected at row {i} during Gauss-Seidel.")

                x[i] = machine.div(numerator, diag)

            # Cálculo do erro: diff = fl(x - x_old)
            diff = [machine.sub(x[i], x_old[i]) for i in range(n)]
            error = infinity_norm(diff, machine)

            # Verifica se houve estagnação numérica causada por mantissa muito curta
            if error == 0 and iteration > 0:
                return {
                    "solution": x,
                    "iterations": iteration + 1,
                    "converged": True,
                    "error": error,
                    "status": "Stagnated (precision limit reached)"
                }

            if error < tol:
                return {
                    "solution": x,
                    "iterations": iteration + 1,
                    "converged": True,
                    "error": error,
                    "status": "Converged"
                }

        except OverflowMachineError:
            return {
                "solution": x,
                "iterations": iteration + 1,
                "converged": False,
                "error": Decimal("1e100"),
                "status": "Diverged due to Machine Overflow"
            }

    return {
        "solution": x,
        "iterations": max_iter,
        "converged": False,
        "error": error,
        "status": "Max iterations reached without convergence"
    }


# =========================================================
# REFERÊNCIA (FLOAT PURO)
# =========================================================

def gauss_seidel_reference(A, b, x0=None, tol=1e-10, max_iter=100):
    """
    Resolve o sistema linear Ax = b pelo método iterativo de Gauss-Seidel
    utilizando a aritmética de dupla precisão nativa do Python (float de 64 bits).
    Usado como controle analítico/ideal para cálculo de erro propagado.

    Entrada:
        A (list[list]), b (list): Dados originais do sistema linear.
        x0 (list, opcional): Vetor de aproximação inicial.
        tol (float): Tolerância de parada.
        max_iter (int): Limite de iterações.
    Saída:
        dict: Relatório com a solução ideal, número de iterações, convergência e erro final.
    """
    n = len(A)

    if x0 is None:
        x = [0.0 for _ in range(n)]
    else:
        x = [float(v) for v in x0]

    A_f = [[float(v) for v in row] for row in A]
    b_f = [float(v) for v in b]

    for iteration in range(max_iter):
        x_old = x.copy()

        for i in range(n):
            sigma = 0.0
            for j in range(n):
                if i != j:
                    sigma += A_f[i][j] * x[j]

            if A_f[i][i] == 0:
                raise ZeroDivisionError(f"Zero diagonal element at row {i} in reference solver.")

            x[i] = (b_f[i] - sigma) / A_f[i][i]

        diff = [x[i] - x_old[i] for i in range(n)]
        error = infinity_norm(diff, machine=None)

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


# Aliases para compatibilidade de chamadas
gauss_seidel = gauss_seidel_finite