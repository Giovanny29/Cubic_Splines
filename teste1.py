import math
from decimal import Decimal
from numerical.machine import FiniteMachine, RoundingMode
from numerical.jacobi import jacobi_finite, jacobi_reference
from numerical.gauss_seidel import gauss_seidel_finite, gauss_seidel_reference
from numerical.convergence import is_diagonally_dominant

def executar_cenario(id_cenario, nome, A, b, x0, tol, max_iter, machine_alta, machine_baixa):
    print(f"\n" + "="*70)
    print(f" CASO DE TESTE {id_cenario}: {nome}")
    print("="*70)
    
    dom = is_diagonally_dominant(A)
    print(f"-> Matriz é estritamente diagonal dominante? {dom}")
    
    # 1. Referência Ideal (Python Float 64-bits)
    ref_j = jacobi_reference(A, b, x0=x0, tol=1e-12, max_iter=max_iter)
    ref_gs = gauss_seidel_reference(A, b, x0=x0, tol=1e-12, max_iter=max_iter)
    print(f"\n--- REFERÊNCIA IDEAL (Float 64-bits) ---")
    print(f" Jacobi      -> Convergiu: {ref_j['converged']:<5} | Iterações: {ref_j['iterations']}")
    print(f" Gauss-Seidel -> Convergiu: {ref_gs['converged']:<5} | Iterações: {ref_gs['iterations']}")
    
    # 2. Máquina de Alta Precisão (t=8)
    alta_j = jacobi_finite(A, b, machine_alta, x0=x0, tol=tol, max_iter=max_iter)
    alta_gs = gauss_seidel_finite(A, b, machine_alta, x0=x0, tol=tol, max_iter=max_iter)
    print(f"\n--- MÁQUINA DE ALTA PRECISÃO F(10, 8, -20, 20) ---")
    print(f" Jacobi      -> Status: {alta_j['status']:<35} | Iterações: {alta_j['iterations']}")
    print(f" Gauss-Seidel -> Status: {alta_gs['status']:<35} | Iterações: {alta_gs['iterations']}")
    
    # 3. Máquina de Baixa Precisão (t=3) - Onde o erro propaga pesado
    baixa_j = jacobi_finite(A, b, machine_baixa, x0=x0, tol=tol, max_iter=max_iter)
    baixa_gs = gauss_seidel_finite(A, b, machine_baixa, x0=x0, tol=tol, max_iter=max_iter)
    print(f"\n--- MÁQUINA DE BAIXA PRECISÃO F(10, 3, -5, 5) ---")
    print(f" Jacobi      -> Status: {baixa_j['status']:<35} | Iterações: {baixa_j['iterations']}")
    if baixa_j['converged'] and baixa_j['error'] != Decimal("1e100"):
        print(f"                Solução obtida: {[float(val) for val in baixa_j['solution']]}")
        
    print(f" Gauss-Seidel -> Status: {baixa_gs['status']:<35} | Iterações: {baixa_gs['iterations']}")
    if baixa_gs['converged'] and baixa_gs['error'] != Decimal("1e100"):
        print(f"                Solução obtida: {[float(val) for val in baixa_gs['solution']]}")

def rodar_mega_bateria():
    machine_alta = FiniteMachine(base=10, precision=8, exponent_min=-20, exponent_max=20)
    machine_baixa = FiniteMachine(base=10, precision=3, exponent_min=-5, exponent_max=5, rounding=RoundingMode.ROUND)
    
    tol = 1e-4
    max_iter = 150

    # -------------------------------------------------------------------------
    # CASO 1: Matriz Comportada (Forte dominância diagonal)
    # Solução: [1.0, 2.0, -1.0]
    # -------------------------------------------------------------------------
    executar_cenario(1, "Forte Dominância Diagonal", 
                     [[5.0, 1.0, 1.0], [1.0, 4.0, 1.0], [1.0, 1.0, 3.0]], 
                     [6.0, 8.0, 0.0], [0.0, 0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 2: Limiar de Convergência (Dominância Diagonal Fraca)
    # Solução: [1.0, 1.0, 1.0]
    # -------------------------------------------------------------------------
    executar_cenario(2, "Dominância Diagonal Fraca", 
                     [[4.0, 2.0, 1.9], [1.9, 4.0, 2.0], [2.0, 1.9, 4.0]], 
                     [7.9, 7.9, 7.9], [0.0, 0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 3: Divergência Catastrófica (Elementos gigantes fora da diagonal)
    # -------------------------------------------------------------------------
    executar_cenario(3, "Divergência Forçada (Sem Dominância)", 
                     [[1.0, 4.0, 5.0], [6.0, 1.0, 3.0], [2.0, 7.0, 1.0]], 
                     [10.0, 10.0, 10.0], [0.0, 0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 4: Comportamento Assimétrico (Gauss-Seidel converge, Jacobi diverge)
    # Solução: [1.0, 1.0, 1.0]
    # -------------------------------------------------------------------------
    executar_cenario(4, "Assimetria Teórica (GS estável, Jacobi instável)", 
                     [[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]], 
                     [2.0, 2.0, 2.0], [0.0, 0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 5: Matriz de Hilbert Modificada (Mal Condicionada)
    # Sistemas mal condicionados sofrem absurdamente com mantissas curtas (t=3)
    # Solução: [1.0, -1.0, 1.0]
    # -------------------------------------------------------------------------
    executar_cenario(5, "Matriz Mal Condicionada (Tipo Hilbert)", 
                     [[1.0, 0.5, 0.333], [0.5, 0.333, 0.25], [0.333, 0.25, 0.2]], 
                     [0.833, 0.583, 0.383], [0.0, 0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 6: Sistema de Grande Porte (Ordem 10x10)
    # Testa se o acúmulo de arredondamentos quebra os métodos em matrizes maiores.
    # Solução: [1.0, 1.0, ..., 1.0]
    # -------------------------------------------------------------------------
    A6 = [[0.0 for _ in range(10)] for _ in range(10)]
    b6 = []
    for i in range(10):
        A6[i][i] = 12.0
        for j in range(10):
            if i != j:
                A6[i][j] = 1.0
        b6.append(21.0)
    executar_cenario(6, "Sistema de Grande Porte (Ordem 10)", 
                     A6, b6, [0.0]*10, tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 7: Matriz Estritamente Esparsa (Muitos zeros)
    # Muito comum em problemas de elementos finitos e Splines!
    # Solução: [1.0, 2.0, 3.0, 4.0]
    # -------------------------------------------------------------------------
    executar_cenario(7, "Matriz Esparsa Tridiagonal", 
                     [[4.0, 1.0, 0.0, 0.0], [1.0, 4.0, 1.0, 0.0], [0.0, 1.0, 4.0, 1.0], [0.0, 0.0, 1.0, 4.0]], 
                     [6.0, 12.0, 18.0, 19.0], [0.0, 0.0, 0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 8: Chute Inicial Distante
    # O chute inicial começa muito longe da solução real para testar robustez.
    # Solução: [2.0, -2.0]
    # -------------------------------------------------------------------------
    executar_cenario(8, "Chute Inicial Muito Distante", 
                     [[8.0, 2.0], [1.0, 5.0]], 
                     [12.0, -8.0], [1000.0, -1000.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 9: Matriz com Diagonal Nula Retificável (Desafio)
    # Tem zero na diagonal do b, mas se houver divisão imediata sem pivotamento, estoura.
    # -------------------------------------------------------------------------
    executar_cenario(9, "Presença de Zero na Diagonal", 
                     [[4.0, 1.0], [0.0, 0.0]], 
                     [5.0, 2.0], [0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

    # -------------------------------------------------------------------------
    # CASO 10: Sistema Singular / Sem Solução Única
    # Linhas linearmente dependentes. Deve falhar de forma limpa ou acusar erro numérico.
    # -------------------------------------------------------------------------
    executar_cenario(10, "Matriz Singular (Dependência Linear)", 
                     [[2.0, 3.0], [4.0, 6.0]], 
                     [5.0, 10.0], [0.0, 0.0], tol, max_iter, machine_alta, machine_baixa)

if __name__ == "__main__":
    rodar_mega_bateria()