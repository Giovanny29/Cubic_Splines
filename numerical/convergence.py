"""
Module: convergence.py
Description: Utilities for convergence analysis of iterative linear system solvers.
"""

def is_diagonally_dominant(A, machine=None):
    """
    Verifica se uma matriz quadrada A é estritamente diagonal dominante por linhas.
    A condição matemática para cada linha i é:
        |A[i][i]| > sum( |A[i][j]| ) para todo j != i

    Entrada:
        A (list[list]): Matriz quadrada de coeficientes do sistema linear.
        machine (FiniteMachine, opcional): Instância da máquina finita para computar 
                                           as somas e módulos sob precisão limitada.
    Saída:
        bool: Retorna True se a matriz for estritamente diagonal dominante,
              e False caso contrário.
    """
    n = len(A)

    for i in range(n):
        # Captura o elemento da diagonal principal
        if machine:
            diagonal = machine.abs(A[i][i])
            row_sum = machine.fl(0)
        else:
            diagonal = abs(A[i][i])
            row_sum = 0

        # Soma os elementos das colunas j (onde j != i)
        for j in range(n):
            if i != j:
                if machine:
                    element_abs = machine.abs(A[i][j])
                    row_sum = machine.add(row_sum, element_abs)
                else:
                    row_sum += abs(A[i][j])

        # Verificação da dominância estrita
        # Se o elemento da diagonal for menor ou igual à soma do restante da linha, falha.
        if diagonal <= row_sum:
            return False

    return True