"""
Module: norms.py
Description: Implementation of vector norms used for convergence criteria 
             and error estimation in iterative methods.
"""
from decimal import Decimal


def infinity_norm(vector, machine=None):
    """
    Calcula a norma infinito (norma do máximo) de um vetor.
    A norma infinito é definida como o maior valor absoluto entre os elementos do vetor:
        ||x||_inf = max( |x_i| )

    Entrada:
        vector (list): Vetor (lista de números ou Decimais) cuja norma será calculada.
        machine (FiniteMachine, opcional): Instância da máquina finita para calcular 
                                           o valor absoluto sob precisão limitada.
    Saída:
        Decimal/float: O valor da norma infinito do vetor. Retorna 0 se o vetor estiver vazio.
    """
    if vector is None or len(vector) == 0:
        return 0

    # =====================================================
    # CASO SEM MÁQUINA (referência ideal / float nativo)
    # =====================================================
    if machine is None:
        return max(abs(float(x)) for x in vector)

    # =====================================================
    # CASO COM MÁQUINA FINITA
    # =====================================================
    max_value = Decimal(0)

    for x in vector:
        try:
            # machine.abs já aplica fl(|x|) e garante o retorno em Decimal
            val = machine.abs(x)
        except Exception:
            # Caso ocorra um overflow catastrófico na máquina, 
            # define um valor representativo muito grande para sinalizar o erro
            val = Decimal("1e100")

        if val > max_value:
            max_value = val

    return max_value