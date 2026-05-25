from decimal import Decimal
from machine import FiniteMachine, RoundingMode
from norms import infinity_norm

def run_norm_tests():
    print("=" * 60)
    print(" INICIANDO TESTES DO MÓDULO DE NORMAS (NORMS.PY)")
    print("=" * 60)

    # Vetor de teste com números positivos, negativos e decimais
    test_vector = [1.5, -4.8, 3.2, -0.1, 4.799]

    # -----------------------------------------------------------------
    # TESTE 1: Sem Máquina (Referência Ideal)
    # -----------------------------------------------------------------
    print("\n[TESTE 1] Calculando Norma Infinito Sem Máquina (Ideal)")
    norm_ideal = infinity_norm(test_vector, machine=None)
    
    print(f"Vetor: {test_vector}")
    print(f"Resultado obtido: {norm_ideal} (Tipo: {type(norm_ideal)})")
    print(f"Resultado esperado: 4.8 (Tipo: Decimal)")
    
    # Validações críticas: o valor correto e a consistência do tipo Decimal
    assert norm_ideal == Decimal('4.8'), "Erro no cálculo da norma infinito ideal."
    assert isinstance(norm_ideal, Decimal), "Erro: O retorno sem máquina deveria ser do tipo Decimal!"

    # -----------------------------------------------------------------
    # TESTE 2: Com Máquina Limitada (Base 10, Precisão 2, ROUND)
    # -----------------------------------------------------------------
    print("\n[TESTE 2] Calculando Norma Infinito Com Máquina Limitada")
    # Criamos uma máquina bem restrita para ver o impacto na norma
    machine_limited = FiniteMachine(base=10, precision=2, rounding=RoundingMode.ROUND)
    
    # O elemento -4.8 ao passar pela máquina continua 4.8 (ou 0.48 x 10^1)
    # O elemento 4.799 ao passar pela máquina vira 4.8 por causa do arredondamento com 2 dígitos!
    norm_machine = infinity_norm(test_vector, machine=machine_limited)
    
    print(f"Resultado obtido com máquina: {norm_machine} (Tipo: {type(norm_machine)})")
    assert norm_machine == Decimal('4.8'), "Erro no cálculo da norma infinito com máquina."
    assert isinstance(norm_machine, Decimal), "Erro: O retorno com máquina deveria ser do tipo Decimal!"

    # -----------------------------------------------------------------
    # TESTE 3: Vetor Vazio ou Nulo
    # -----------------------------------------------------------------
    print("\n[TESTE 3] Validação de Vetor Vazio")
    norm_empty = infinity_norm([], machine=None)
    print(f"Resultado para vetor vazio: {norm_empty}")
    assert norm_empty == Decimal('0'), "Erro: Vetor vazio deveria retornar Decimal(0)."

    # -----------------------------------------------------------------
    # TESTE 4: Simulação de Overflow Catastrófico (Teste de Estresse)
    # -----------------------------------------------------------------
    print("\n[TESTE 4] Validação de Resiliência a Overflow na Norma")
    # Criamos uma máquina com expoente máximo minúsculo (k2 = 1)
    machine_overflow = FiniteMachine(base=10, precision=2, exponent_max=1, rounding=RoundingMode.ROUND)
    
    # O número 500.0 precisa de expoente 3 (0.5 x 10^3), o que vai estourar o limite (k2=1)
    vector_with_large_num = [1.0, 500.0, 2.0]
    
    norm_overflow = infinity_norm(vector_with_large_num, machine=machine_overflow)
    print(f"Resultado obtido sob overflow: {norm_overflow} (Esperado: 1e+100)")
    assert norm_overflow == Decimal("1e100"), "A norma não tratou o overflow de forma resiliente."

if __name__ == "__main__":
    run_norm_tests()