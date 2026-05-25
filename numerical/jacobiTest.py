"""
Module: test_jacobi_completissimo.py
Description: Bateria exaustiva de testes (12 casos) para homologação rigorosa
             do algoritmo Jacobi (Aritmética Limitada vs Referência Ideal).
"""
import math
from decimal import Decimal
from machine import FiniteMachine, RoundingMode
from jacobi import jacobi_finite, jacobi_reference

def run_exhaustive_tests():
    print("=" * 80)
    print(" 🔥 BATERIA DE HOMOLOGAÇÃO EXAUSTIVA DO SOLVER JACOBI (12 CASOS)")
    print("=" * 80)
    
    success_count = 0

    # -----------------------------------------------------------------
    # CATEGORIA A: MATRIZES TIPICAMENTE DE SPLINES (DIAGONAL DOMINANTE)
    # -----------------------------------------------------------------
    # Caso 1: Sistema clássico de Spline Cúbica Natural (Matriz Tridiagonal 3x3)
    # 4M_1 + M_2 = b_1, etc.
    A1 = [[4.0, 1.0, 0.0],
          [1.0, 4.0, 1.0],
          [0.0, 1.0, 4.0]]
    b1 = [5.0, 6.0, 5.0]  # Solução teórica: [1.0, 1.0, 1.0]

    print("\n[CASO 1] Matriz Tridiagonal de Spline Cúbica (Média Precisão)")
    m = FiniteMachine(base=10, precision=4, rounding=RoundingMode.ROUND)
    res = jacobi_finite(A1, b1, machine=m, tol=1e-3)
    print(f"-> Status: {res['status']} | Iterações: {res['iterations']} | Solução: {res['solution']}")
    assert res['converged'] and res['status'] == "Converged", "Falha no Caso 1"
    success_count += 1

    # Caso 2: Sistema de Spline com valores de coordenadas altos (Teste de Escala)
    b2 = [500.0, 600.0, 500.0]  # Solução teórica: [100.0, 100.0, 100.0]
    print("\n[CASO 2] Sistema de Spline com Alta Escala (Teste do Erro Relativo)")
    res = jacobi_finite(A1, b2, machine=m, tol=1e-3)
    print(f"-> Status: {res['status']} | Iterações: {res['iterations']} | Solução: {res['solution']}")
    assert res['converged'] and res['status'] == "Converged", "Falha no Caso 2"
    success_count += 1

    # Caso 3: Matriz de ordem maior (5x5) estritamente diagonal dominante
    A3 = [[5.0, 1.0, 0.0, 0.0, 0.0],
          [1.0, 5.0, 1.0, 0.0, 0.0],
          [0.0, 1.0, 5.0, 1.0, 0.0],
          [0.0, 0.0, 1.0, 5.0, 1.0],
          [0.0, 0.0, 0.0, 1.0, 5.0]]
    b3 = [6.0, 7.0, 7.0, 7.0, 6.0]  # Solução: [1.0, 1.0, 1.0, 1.0, 1.0]
    print("\n[CASO 3] Matriz Tridiagonal Expandida 5x5 (Estrutura de Malha)")
    res = jacobi_finite(A3, b3, machine=m, tol=1e-4)
    print(f"-> Status: {res['status']} | Iterações: {res['iterations']}")
    assert res['converged'], "Falha no Caso 3"
    success_count += 1

    # -----------------------------------------------------------------
    # CATEGORIA B: CENÁRIOS DE LIMITAÇÃO DE PROXIMIDADE (MANTISSA CURTA)
    # -----------------------------------------------------------------
    # Caso 4: Estagnação clássica provocada por mantissa de 2 dígitos
    print("\n[CASO 4] Forçando Estagnação Numérica Consciente (t=2)")
    m_curta = FiniteMachine(base=10, precision=2, rounding=RoundingMode.ROUND)
    res = jacobi_finite(A1, b1, machine=m_curta, tol=1e-5)
    print(f"-> Status: {res['status']} | Solução Estagnada: {res['solution']}")
    assert res['status'] == "Stagnated (Precision limit reached)", "Falha no Caso 4"
    success_count += 1

    # Caso 5: Truncamento seco em vez de Arredondamento com pouca mantissa
    print("\n[CASO 5] Forçando Estagnação em Modo TRUNCATE (t=3)")
    m_trunc = FiniteMachine(base=10, precision=3, rounding=RoundingMode.TRUNCATE)
    res = jacobi_finite(A1, b1, machine=m_trunc, tol=1e-5)
    print(f"-> Status: {res['status']} | Iterações até travar: {res['iterations']}")
    assert res['status'] == "Stagnated (Precision limit reached)" or res['converged'], "Falha no Caso 5"
    success_count += 1

    # -----------------------------------------------------------------
    # CATEGORIA C: CASOS EXTREMOS, FALHAS E EXCEÇÕES DE ÁLGEBRA
    # -----------------------------------------------------------------
    # Caso 6: Elemento zero na diagonal principal (Impossibilidade matemática imediata)
    A6 = [[0.0, 2.0], 
          [1.0, 3.0]]
    b6 = [2.0, 4.0]
    print("\n[CASO 6] Interceptação de Elemento Nulo na Diagonal")
    try:
        jacobi_finite(A6, b6, machine=m)
        print("-> Falha: Deveria ter lançado ZeroDivisionError")
        assert False
    except ZeroDivisionError:
        print("-> Sucesso: Erro de divisão por zero na diagonal capturado perfeitamente.")
        success_count += 1

    # Caso 7: Divergência por falta de dominância com estouro por Overflow
    A7 = [[1.0, 10.0], 
          [10.0, 1.0]]
    b7 = [11.0, 11.0]
    print("\n[CASO 7] Sistema Divergente com Disparo de Overflow")
    m_low_exp = FiniteMachine(base=10, precision=4, exponent_max=8, rounding=RoundingMode.ROUND)
    res = jacobi_finite(A7, b7, machine=m_low_exp, tol=1e-3, max_iter=100)
    print(f"-> Status: {res['status']} | Iterações: {res['iterations']}")
    assert res['status'] == "Diverged due to Machine Overflow" and not res['converged'], "Falha no Caso 7"
    success_count += 1

    # Caso 8: Sistema Divergente que atinge o limite máximo de iterações sem explodir
    print("\n[CASO 8] Sistema Divergente Controlado (Atinge Máximo de Iterações)")
    m_high_exp = FiniteMachine(base=10, precision=4, exponent_max=100, rounding=RoundingMode.ROUND)
    res = jacobi_finite(A7, b7, machine=m_high_exp, tol=1e-3, max_iter=15)
    print(f"-> Status: {res['status']} | Iterações executadas: {res['iterations']}")
    assert res['status'] == "Max iterations reached without convergence", "Falha no Caso 8"
    success_count += 1

    # -----------------------------------------------------------------
    # CATEGORIA D: CASOS DE BASE EXÓTICA E COERÊNCIA ANALÍTICA
    # -----------------------------------------------------------------
    # Caso 9: Teste de fogo na Base Binária (Base 2, t=8)
    print("\n[CASO 9] Execução em Máquina Binária Simulada (Base 2, t=8)")
    m_bin = FiniteMachine(base=2, precision=8, rounding=RoundingMode.ROUND)
    res = jacobi_finite(A1, b1, machine=m_bin, tol=1e-3)
    print(f"-> Status: {res['status']} | Solução convertida da Base 2: {res['solution']}")
    assert res['converged'], "Falha no Caso 9"
    success_count += 1

    # Caso 10: Comparação direta com a Solução de Referência Ideal (Validação Cruzada)
    print("\n[CASO 10] Validação Cruzada: Solução de Máquina vs Solução de Referência")
    res_machine = jacobi_finite(A1, b1, machine=m, tol=1e-5, max_iter=50)
    res_ref = jacobi_reference(A1, b1, tol=1e-10, max_iter=50)
    
    # Compara a distância absoluta dos vetores finais das duas soluções
    diffs = [abs(float(res_machine['solution'][i]) - res_ref['solution'][i]) for i in range(len(b1))]
    max_diff = max(diffs)
    print(f"-> Desvio Máximo da Máquina Limitada frente ao Ideal: {max_diff:.8f}")
    assert max_diff < 1e-2, "O desvio entre máquina e referência ideal está fora do esperado."
    success_count += 1

    # Caso 11: Chute inicial perfeito (Vetor x0 já é a solução exata)
    print("\n[CASO 11] Convergência Imediata com Chute Inicial Perfeito")
    res = jacobi_finite(A1, b1, machine=m, x0=[1.0, 1.0, 1.0], tol=1e-4)
    print(f"-> Status: {res['status']} | Iterações necessárias: {res['iterations']}")
    assert res['iterations'] == 1, "Deveria convergir na primeira iteração com chute perfeito."
    success_count += 1

    # Caso 12: Sistema com termos independentes nulos (Vetor b cheio de zeros)
    print("\n[CASO 12] Sistema Homogêneo (Vetor B nulo)")
    res = jacobi_finite(A1, [0.0, 0.0, 0.0], machine=m, x0=[0.5, -0.5, 0.2], tol=1e-4)
    print(f"-> Status: {res['status']} | Solução final: {res['solution']}")
    assert res['converged'] and abs(res['solution'][0]) < 1e-3, "Falha no Caso 12"
    success_count += 1

    # -----------------------------------------------------------------
    # BALANÇO FINAL
    # -----------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f" 📊 RELATÓRIO DE HOMOLOGAÇÃO: {success_count}/12 CASOS PASSARAM COM SUCESSO.")
    print("=" * 80)
    if success_count == 12:
        print(" 🎉 O SOLVER JACOBI FOI 100% HOMOLOGADO PARA PRODUÇÃO!")
    print("=" * 80)

if __name__ == "__main__":
    run_exhaustive_tests()