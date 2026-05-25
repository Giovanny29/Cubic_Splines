"""
Module: jacobi.py
Description: Implementation of the Jacobi Iterative Method for solving linear systems 
             using both finite machine arithmetic and ideal reference arithmetic,
             integrated with convergence analysis.
"""
from decimal import Decimal
from numerical.norms import infinity_norm
from numerical.machine import OverflowMachineError
from numerical.convergence import is_diagonally_dominant

# =========================================================
# JACOBI COM MÁQUINA FINITA (EXPERIMENTAL)
# =========================================================

def jacobi_finite(A, b, machine, x0=None, tol=1e-6, max_iter=100):
    """
    Resolve o sistema linear Ax = b pelo método iterativo de Jacobi
    utilizando estritamente a aritmética limitada da máquina finita.

    Entrada:
        A (list[list]): Matriz de coeficientes do sistema.
        b (list): Vetor de termos independentes.
        machine (FiniteMachine): Instância da máquina virtual para processamento aritmético.
        x0 (list, opcional): Vetor de aproximação inicial. Se None, inicializa com zeros.
        tol (float): Tolerância para o critério de parada baseada no erro relativo.
        max_iter (int): Número máximo de iterações permitidas.
    Saída:
        dict: Relatório contendo os dados de convergência, estabilidade e a solução obtida.
    """
    if machine is None:
        raise ValueError("FiniteMachine não fornecida ao jacobi_finite.")

    n = len(A)

    # Conversão das estruturas para representação interna da máquina
    A_m = machine.matrix(A)
    b_m = machine.vector(b)

    # Análise prévia de convergência baseada na aritmética da máquina
    is_dominant = is_diagonally_dominant(A_m, machine)

    if x0 is None:
        x = [machine.fl(0) for _ in range(n)]
    else:
        x = machine.vector(x0)

    error = machine.fl(0)
    tol_m = machine.fl(tol)

    for iteration in range(max_iter):
        x_new = [machine.fl(0) for _ in range(n)]

        try:
            # Passo de Predição do Jacobi
            for i in range(n):
                sigma = machine.fl(0)

                for j in range(n):
                    if i != j:
                        term = machine.mul(A_m[i][j], x[j])
                        sigma = machine.add(sigma, term)

                numerator = machine.sub(b_m[i], sigma)
                diag = A_m[i][i]

                if diag == 0:
                    raise ZeroDivisionError(f"Elemento diagonal nulo detectado na linha {i} durante o Jacobi.")

                x_new[i] = machine.div(numerator, diag)

            # Cálculo do vetor de diferenças absolutas: diff = fl(x_new - x)
            diff = [machine.sub(x_new[i], x[i]) for i in range(n)]
            abs_error = infinity_norm(diff, machine)
            
            # Cálculo da norma do novo vetor para o erro relativo
            norm_x_new = infinity_norm(x_new, machine)

            # Cálculo do Erro Relativo na Máquina
            if norm_x_new != 0:
                error = machine.div(abs_error, norm_x_new)
            else:
                error = abs_error

            # Verifica se houve estagnação numérica (mudança nula por perda de precisão)
            if abs_error == 0 and iteration > 0:
                return {
                    "solution": x_new,
                    "iterations": iteration + 1,
                    "converged": True,
                    "diagonally_dominant": is_dominant,
                    "error": error,
                    "status": "Stagnated (Precision limit reached)"
                }

            # Atualiza o vetor de estados
            x = x_new

            # Critério de Parada Relativo
            if error < tol_m:
                return {
                    "solution": x,
                    "iterations": iteration + 1,
                    "converged": True,
                    "diagonally_dominant": is_dominant,
                    "error": error,
                    "status": "Converged"
                }

        except OverflowMachineError:
            return {
                "solution": x,
                "iterations": iteration + 1,
                "converged": False,
                "diagonally_dominant": is_dominant,
                "error": Decimal("1e100"),
                "status": "Diverged due to Machine Overflow"
            }

    return {
        "solution": x,
        "iterations": max_iter,
        "converged": False,
        "diagonally_dominant": is_dominant,
        "error": error,
        "status": "Max iterations reached without convergence"
    }


# =========================================================
# JACOBI DE REFERÊNCIA (IDEAL / SEM MÁQUINA FINITA)
# =========================================================

def jacobi_reference(A, b, x0=None, tol=1e-10, max_iter=100):
    """
    Resolve o sistema linear Ax = b pelo método de Jacobi em dupla precisão nativa (float 64-bit).
    """
    n = len(A)

    # Análise prévia de convergência ideal
    is_dominant = is_diagonally_dominant(A, machine=None)

    if x0 is None:
        x0 = [0.0 for _ in range(n)]

    x = [float(v) for v in x0]
    b_f = [float(v) for v in b]
    A_f = [[float(v) for v in row] for row in A]

    for iteration in range(max_iter):
        x_new = [0.0 for _ in range(n)]

        for i in range(n):
            sigma = 0.0
            for j in range(n):
                if i != j:
                    sigma += A_f[i][j] * x[j]

            if A_f[i][i] == 0:
                raise ZeroDivisionError(f"Elemento diagonal nulo na linha {i} no solver de referência.")

            x_new[i] = (b_f[i] - sigma) / A_f[i][i]

        # Erro Relativo na referência ideal
        diff = [x_new[i] - x[i] for i in range(n)]
        abs_error = infinity_norm(diff, machine=None)
        norm_x_new = infinity_norm(x_new, machine=None)
        
        error = abs_error / norm_x_new if norm_x_new != 0 else abs_error

        x = x_new

        if error < tol:
            return {
                "solution": x,
                "iterations": iteration + 1,
                "converged": True,
                "diagonally_dominant": is_dominant,
                "error": error
            }

    return {
        "solution": x,
        "iterations": max_iter,
        "converged": False,
        "diagonally_dominant": is_dominant,
        "error": error
    }