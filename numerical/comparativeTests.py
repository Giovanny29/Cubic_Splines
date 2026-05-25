"""
Module: comparativeTests.py
Description: Script de validação cruzada e comparação de desempenho iterativo
             entre os métodos de Jacobi e Gauss-Seidel sob aritmética finita.
"""
"""
Module: comparativeTests.py
Description: Script de validação cruzada e comparação de desempenho iterativo
             entre os métodos de Jacobi e Gauss-Seidel sob aritmética finita.
"""
import math
from decimal import Decimal
from machine import FiniteMachine, RoundingMode
from gauss_seidel import gauss_seidel_finite, gauss_seidel_reference

def run_seidel_exhaustive_tests():
    print("=" * 85)
    print(" ⚡ BATERIA DE HOMOLOGAÇÃO EXAUSTIVA: GAUSS-SEIDEL PARA MATRIZES DE ORDEM MAIOR")
    print("=" * 85)
    
    success_count = 0
    m_padrao = FiniteMachine(base=10, precision=5, rounding=RoundingMode.ROUND)

    # -----------------------------------------------------------------
    # CASO 1: Matriz 4x4 Estritamente Diagonal Dominante
    # -----------------------------------------------------------------
    print("\n[CASO 1] Matriz 4x4 de Ordem Maior (Precisão t=5)")
    try:
        A1 = [[10.0, -1.0, 2.0, 0.0],
              [-1.0, 11.0, -1.0, 3.0],
              [2.0, -1.0, 10.0, -1.0],
              [0.0, 3.0, -1.0, 8.0]]
        b1 = [6.0, 25.0, -11.0, 15.0]
        
        res = gauss_seidel_finite(A1, b1, machine=m_padrao, tol=1e-4)
        print(f"-> Status: {res['status']} | Iterações: {res['iterations']} | Solução: {res['solution']}")
        assert res['converged'], "Falha no Caso 1: O sistema deveria ter convergido."
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 1 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 2: Matriz 5x5 de Spline Cúbica Expandida (Alta Escala)
    # -----------------------------------------------------------------
    print("\n[CASO 2] Matriz de Malha de Spline 5x5 em Larga Escala (Erro Relativo)")
    try:
        A2 = [[4.0, 1.0, 0.0, 0.0, 0.0],
              [1.0, 4.0, 1.0, 0.0, 0.0],
              [0.0, 1.0, 4.0, 1.0, 0.0],
              [0.0, 0.0, 1.0, 4.0, 1.0],
              [0.0, 0.0, 0.0, 1.0, 4.0]]
        b2 = [1000.0, 2000.0, 2000.0, 2000.0, 1000.0]
        
        res = gauss_seidel_finite(A2, b2, machine=m_padrao, tol=1e-4)
        print(f"-> Status: {res['status']} | Iterações: {res['iterations']} | Solução: {res['solution']}")
        assert res['converged'], "Falha no Caso 2: O sistema em larga escala deveria ter convergido."
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 2 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 3: Teste de Estresse - Matriz de Ordem 10x10 (Tridiagonal)
    # -----------------------------------------------------------------
    print("\n[CASO 3] Teste de Carga Extrema: Sistema Tridiagonal 10x10")
    try:
        n_large = 10
        A3 = [[0.0 for _ in range(n_large)] for _ in range(n_large)]
        for i in range(n_large):
            A3[i][i] = 4.0
            if i > 0: A3[i][i-1] = 1.0
            if i < n_large - 1: A3[i][i+1] = 1.0
        b3 = [6.0 if (0 < i < n_large-1) else 5.0 for i in range(n_large)]
        
        res = gauss_seidel_finite(A3, b3, machine=m_padrao, tol=1e-4, max_iter=200)
        print(f"-> Status: {res['status']} | Iterações: {res['iterations']} | Solução: {res['solution']}")
        assert res['converged'], "Falha no Caso 3: O sistema 10x10 deveria ter convergido."
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 3 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 4: Matriz 4x4 Dominante por Pouco (Limiar de Estagnação t=3)
    # -----------------------------------------------------------------
    print("\n[CASO 4] Matriz 4x4 de Convergência Lenta com Mantissa Curta (t=3, TRUNCATE)")
    try:
        A4 = [[3.0, 1.0, 1.0, 0.9],
              [1.0, 3.0, 0.9, 1.0],
              [1.0, 0.9, 3.0, 1.0],
              [0.9, 1.0, 1.0, 3.0]]
        b4 = [5.9, 5.9, 5.9, 5.9]
        
        m_curta = FiniteMachine(base=10, precision=3, rounding=RoundingMode.TRUNCATE)
        res = gauss_seidel_finite(A4, b4, machine=m_curta, tol=1e-4)
        print(f"-> Status: {res['status']} | Iterações até parar: {res['iterations']} | Solução obtida: {res['solution']}")
        assert res['status'] == "Stagnated (Precision limit reached)" or res['converged'], "Falha no Caso 4"
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 4 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 5: Validação Cruzada de Ordem Maior (Máquina vs Referência Float64)
    # -----------------------------------------------------------------
    print("\n[CASO 5] Validação Cruzada 4x4: Desvio Máximo vs Referência Ideal")
    try:
        res_m = gauss_seidel_finite(A1, b1, machine=m_padrao, tol=1e-6, max_iter=50)
        res_r = gauss_seidel_reference(A1, b1, tol=1e-12, max_iter=50)
        
        diffs = [abs(float(res_m['solution'][i]) - res_r['solution'][i]) for i in range(4)]
        max_diff = max(diffs)
        print(f"-> Desvio Máximo medido: {max_diff:.8f}")
        print(f"  └─ Solução Máquina:    {res_m['solution']}")
        print(f"  └─ Solução Referência: {res_r['solution']}")
        assert max_diff < 1e-3, "Desvio muito alto entre máquina e float ideal."
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 5 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 6: Matriz de Ordem 6x6 de Crescimento Explosivo (Divergência)
    # -----------------------------------------------------------------
    print("\n[CASO 6] Matriz 6x6 Divergente (Gatilhando Overflow de Expoente K2)")
    try:
        A6 = [[1.0, 50.0, 50.0, 50.0, 50.0, 50.0] for _ in range(6)]
        b6 = [1.0 for _ in range(6)]
        
        m_low_exp = FiniteMachine(base=10, precision=6, exponent_max=8, rounding=RoundingMode.ROUND)
        res = gauss_seidel_finite(A6, b6, machine=m_low_exp, tol=1e-4, max_iter=50)
        print(f"-> Status do estouro: {res['status']} | Parou na iteração: {res['iterations']} | Último estado de X: {res['solution']}")
        assert res['status'] == "Diverged due to Machine Overflow", "Falha no Caso 6: Deveria ter estourado o expoente."
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 6 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 7: Chute Inicial idêntico à Solução em Matriz 4x4
    # -----------------------------------------------------------------
    print("\n[CASO 7] Chute Inicial Perfeito em Sistema 4x4")
    try:
        res = gauss_seidel_finite(A1, b1, machine=m_padrao, x0=[1.0, 2.0, -1.0, 1.0], tol=1e-4)
        print(f"-> Iterações necessárias: {res['iterations']} | Solução: {res['solution']}")
        assert res['iterations'] == 1, "Deveria liquidar na primeira iteração."
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 7 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 8: Sistema Homogêneo de Ordem 5x5 (Vetor b Zerado)
    # -----------------------------------------------------------------
    print("\n[CASO 8] Sistema Homogêneo 5x5 com Chute Inicial Arbitrário")
    try:
        b_zero = [0.0, 0.0, 0.0, 0.0, 0.0]
        res = gauss_seidel_finite(A2, b_zero, machine=m_padrao, x0=[9.0, -5.0, 2.0, 1.5, -3.0], tol=1e-4)
        print(f"-> Status: {res['status']} | Iterações: {res['iterations']} | Solução final: {res['solution']}")
        assert res['converged'] and abs(res['solution'][0]) < 1e-3, "Falha no Caso 8"
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 8 FALHOU: {e}")

    # -----------------------------------------------------------------
    # CASO 9: Elemento Zero na Diagonal de Matriz de Ordem 4x4
    # -----------------------------------------------------------------
    print("\n[CASO 9] Interceptação de Zero na Diagonal em Sistema 4x4")
    try:
        A9 = [[1.0, 2.0, 3.0, 4.0],
              [0.0, 0.0, 2.0, 1.0],
              [1.0, 1.0, 5.0, 1.0],
              [0.0, 0.0, 1.0, 4.0]]
        b9 = [10.0, 3.0, 8.0, 5.0]
        
        gauss_seidel_finite(A9, b9, machine=m_padrao)
        print("-> Erro: Permitiu divisão por zero sem disparar exceção!")
        assert False
    except ZeroDivisionError as e:
        print(f"-> Sucesso: Exceção capturada perfeitamente: '{e}'")
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 9 FALHOU com erro inesperado: {e}")

    # -----------------------------------------------------------------
    # CASO 10: Execução em Máquina Hexadecimal Simulada (Base 16, t=4)
    # -----------------------------------------------------------------
    print("\n[CASO 10] Execução do Sistema 4x4 em Arquitetura Hexadecimal (Base 16, t=4)")
    try:
        m_hex = FiniteMachine(base=16, precision=4, rounding=RoundingMode.ROUND)
        res = gauss_seidel_finite(A1, b1, machine=m_hex, tol=1e-4)
        print(f"-> Status: {res['status']} | Iterações: {res['iterations']} | Solução convertida: {res['solution']}")
        assert res['converged'], "Falha no Caso 10"
        success_count += 1
    except Exception as e:
        print(f"❌ CASO 10 FALHOU: {e}")

    # -----------------------------------------------------------------
    # BALANÇO FINAL
    # -----------------------------------------------------------------
    print("\n" + "=" * 85)
    print(f" 📊 RELATÓRIO DE HOMOLOGAÇÃO DO GAUSS-SEIDEL: {success_count}/10 CASOS CONCLUÍDOS.")
    print("=" * 85)
    if success_count == 10:
        print(" 🎉 O SOLVER GAUSS-SEIDEL FOI 100% HOMOLOGADO PARA MATRIZES DE ORDENS MAIORES!")
    else:
        print(f" ⚠️ ATENÇÃO: {10 - success_count} CENÁRIO(S) APRESENTOU(ARAM) COMPORTAMENTO NUMÉRICO DIVERGENTE.")
    print("=" * 85)

if __name__ == "__main__":
    run_seidel_exhaustive_tests()