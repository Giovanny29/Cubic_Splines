"""
Script de Homologação Avançado: test_spline_completo.py
Valida múltiplos cenários e compara Gauss-Seidel vs Jacobi na Máquina Finita.
"""
from numerical.machine import FiniteMachine  
from spline.spline_builder import build_natural_spline
from spline.spline_evaluator import SplineEvaluator

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

def exibir_tabela_pontos(titulo, x_testes, y_esperados, eval_ref, eval_fin):
    print(f"\n   📊 Verificação de Pontos Internos - {titulo}:")
    print(f"      {'X':<6} | {'Esperado':<10} | {'NumPy (Ref)':<12} | {'Máquina Finita':<14} | {'Status'}")
    print(f"      " + "-" * 65)
    for x, y_exp in zip(x_testes, y_esperados):
        y_ref = eval_ref.evaluate(x)
        y_fin = eval_fin.evaluate(x)
        diff = abs(y_fin - y_ref)
        status = "✅ OK" if diff < 1e-4 else "⚠️ DIF"
        print(f"      {x:<6.2f} | {y_exp:<10.4f} | {y_ref:<12.4f} | {y_fin:<14.4f} | {status}")

def executar_bateria_testes():
    print("=" * 80)
    print("🚀 BATERIA DE TESTES GLOBAIS: CONVERGÊNCIA E PRECISÃO DAS SPLINES")
    print("=" * 80)

    # Inicializa a máquina com precisão controlada (Ex: 7 dígitos de mantissa)
    try:
        machine = FiniteMachine(digits=7, max_exponent=10)
        print("⚙️  Máquina simulada inicializada com Mantissa t = 7.")
    except:
        machine = FiniteMachine()
        print("⚙️  Máquina simulada inicializada com configurações padrão.")

    # -------------------------------------------------------------------------
    # CENÁRIO 1: O Caso Cúbico Simétrico (4 Pontos) - O que calculamos no papel!
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("🔹 CENÁRIO 1: 4 Pontos Simétricos (Curva Suave)")
    print("-" * 80)
    c1_points = [Point(0, 0), Point(1, 1), Point(2, 1), Point(3, 0)]
    c1_x_test = [0.0, 0.5, 1.5, 2.5, 3.0]
    c1_y_exp  = [0.0, 0.5250, 1.1250, 0.5250, 0.0] # 1.1250 no ponto médio!

    for miodo in ["gauss", "jacobi"]:
        res = build_natural_spline(c1_points, machine=machine, method=miodo)
        fin = res["finite"]
        print(f"▶ Método: {miodo.upper():<12} | Convergiu: {str(fin['converged']):<5} | Iterações: {fin['iterations']:<3} | Erro Final: {fin['error']:.2e}")
        
        eval_ref = SplineEvaluator(res["segments_reference"])
        eval_fin = SplineEvaluator(res["segments_finite"])
        exibir_tabela_pontos(miodo.upper(), c1_x_test, c1_y_exp, eval_ref, eval_fin)

    # -------------------------------------------------------------------------
    # CENÁRIO 2: Oscilação / Zigue-Zague (5 Pontos) - Força mais iterações
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("🔹 CENÁRIO 2: 5 Pontos em Zigue-Zague (Perfil de Onda)")
    print("-" * 80)
    c2_points = [Point(0, 0), Point(1, 2), Point(2, -1), Point(3, 3), Point(4, 0)]
    c2_x_test = [0.5, 1.5, 2.5, 3.5]
    c2_y_exp  = [1.0938, 0.5156, 0.6094, 1.9844] # Valores teóricos de ref

    for miodo in ["gauss", "jacobi"]:
        res = build_natural_spline(c2_points, machine=machine, method=miodo)
        fin = res["finite"]
        print(f"▶ Método: {miodo.upper():<12} | Convergiu: {str(fin['converged']):<5} | Iterações: {fin['iterations']:<3} | Erro Final: {fin['error']:.2e}")
        
        eval_ref = SplineEvaluator(res["segments_reference"])
        eval_fin = SplineEvaluator(res["segments_finite"])
        exibir_tabela_pontos(miodo.upper(), c2_x_test, c2_y_exp, eval_ref, eval_fin)

    # -------------------------------------------------------------------------
    # CENÁRIO 3: Teste de Estresse por Acúmulo Erro (7 Pontos)
    # -------------------------------------------------------------------------
    print("\n" + "-" * 80)
    print("🔹 CENÁRIO 3: Crescimento Monotônico (7 Pontos)")
    print("-" * 80)
    c3_points = [Point(0, 0), Point(1, 1), Point(2, 4), Point(3, 9), Point(4, 16), Point(5, 25), Point(6, 36)]
    c3_x_test = [0.5, 2.5, 5.5]
    c3_y_exp  = [0.4464, 6.2500, 30.3036]

    for miodo in ["gauss", "jacobi"]:
        res = build_natural_spline(c3_points, machine=machine, method=miodo)
        fin = res["finite"]
        print(f"▶ Método: {miodo.upper():<12} | Convergiu: {str(fin['converged']):<5} | Iterações: {fin['iterations']:<3} | Erro Final: {fin['error']:.2e}")
        
        eval_ref = SplineEvaluator(res["segments_reference"])
        eval_fin = SplineEvaluator(res["segments_finite"])
        exibir_tabela_pontos(miodo.upper(), c3_x_test, c3_y_exp, eval_ref, eval_fin)

    print("\n" + "=" * 80)
    print("🎉 FIM DA BATERIA DE HOMOLOGAÇÃO!")
    print("=" * 80)

if __name__ == "__main__":
    executar_bateria_testes()