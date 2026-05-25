"""
Module: convergence.py
Description: Utilities for convergence analysis of iterative linear system solvers.
"""
from decimal import Decimal

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
        # =====================================================
        # FLUXO COM MÁQUINA FINITA
        # =====================================================
        if machine:
            diagonal = machine.abs(A[i][i])
            row_sum = Decimal('0')  # Base limpa para o acumulador da máquina

            for j in range(n):
                if i != j:
                    element_abs = machine.abs(A[i][j])
                    row_sum = machine.add(row_sum, element_abs)

        # =====================================================
        # FLUXO SEM MÁQUINA (Referência Ideal)
        # =====================================================
        else:
            # Garante consistência convertendo para Decimal de alta precisão
            diagonal = Decimal(str(A[i][i])).copy_abs()
            row_sum = Decimal('0')

            for j in range(n):
                if i != j:
                    row_sum += Decimal(str(A[i][j])).copy_abs()

        # =====================================================
        # VERIFICAÇÃO DA DOMINÂNCIA ESTRITA
        # =====================================================
        # Funciona perfeitamente para ambos os fluxos, pois ambos os retornos
        # agora usam comparadores numéricos limpos do ecossistema Decimal.
        if diagonal <= row_sum:
            return False

    return True