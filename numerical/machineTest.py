from decimal import Decimal
from machine import FiniteMachine, RoundingMode

def run_tests():
    print("=" * 60)
    print(" INICIANDO TESTES DA FINITE MACHINE (MANTISSA CORRIGIDA)")
    print("=" * 60)

    # -----------------------------------------------------------------
    # TESTE 1: Base 10 - Arredondamento Padrão (ROUND)
    # -----------------------------------------------------------------
    print("\n[TESTE 1] Base 10, 4 Dígitos, Modo ROUND")
    m10_round = FiniteMachine(base=10, precision=4, rounding=RoundingMode.ROUND)
    
    # 0.12345 -> Deve arredondar para cima -> 0.1235
    v1 = m10_round.fl(0.12345)
    print(f"Entrada: 0.12345 | fl(x): {v1} (Esperado: 0.1235)")
    assert v1 == Decimal('0.1235'), "Erro no arredondamento para cima (Base 10)"

    # 0.12344 -> Deve arredondar para baixo -> 0.1234
    v2 = m10_round.fl(0.12344)
    print(f"Entrada: 0.12344 | fl(x): {v2} (Esperado: 0.1234)")
    assert v2 == Decimal('0.1234'), "Erro no arredondamento para baixo (Base 10)"

    # -----------------------------------------------------------------
    # TESTE 2: Base 10 - Truncamento (TRUNCATE)
    # -----------------------------------------------------------------
    print("\n[TESTE 2] Base 10, 4 Dígitos, Modo TRUNCATE")
    m10_trunc = FiniteMachine(base=10, precision=4, rounding=RoundingMode.TRUNCATE)
    
    # Mesmo com fim '5', deve cortar seco -> 0.1234
    v3 = m10_trunc.fl(0.1234999)
    print(f"Entrada: 0.1234999 | fl(x): {v3} (Esperado: 0.1234)")
    assert v3 == Decimal('0.1234'), "Erro no truncamento (Base 10)"

    # -----------------------------------------------------------------
    # TESTE 3: Base 2 (Binária) - O Teste de Fogo do Arredondamento
    # -----------------------------------------------------------------
    print("\n[TESTE 3] Base 2, 3 Dígitos de Mantissa, Modo ROUND")
    m2_round = FiniteMachine(base=2, precision=3, rounding=RoundingMode.ROUND)
    
    # Em base 2 com t=3:
    # 0.625 em decimal é exatamente 0.101 em binário (já tem 3 dígitos significativos)
    # 0.6875 em decimal é exatamente 0.1011 em binário (4 dígitos). 
    # O quarto dígito é '1' (que é >= b/2, ou seja, >= 1 em binário), então deve arredondar para cima!
    # 0.1011 + 0.0001 = 0.110 em binário, que equivale a 0.75 em decimal.
    
    v_base2 = m2_round.fl(0.6875)
    print(f"Entrada Decimal: 0.6875 (Binário: 0.1011)")
    print(f"Resultado fl(x) em Decimal: {v_base2} (Esperado: 0.75, que é Binário: 0.110)")
    
    # Exibição visual dos dígitos na base 2
    print("Representação interna na máquina:")
    m2_round.print_machine_number(0.6875)
    
    assert v_base2 == Decimal('0.75'), "Erro no arredondamento multibase (Base 2)"

    # -----------------------------------------------------------------
    # TESTE 4: Estouro de Mantissa por Arredondamento (0.99999 -> 1.0)
    # -----------------------------------------------------------------
    print("\n[TESTE 4] Renormalização após arredondamento (Estouro de Mantissa)")
    m10_edge = FiniteMachine(base=10, precision=3, rounding=RoundingMode.ROUND)
    
    # 0.9996 -> Arredonda para 1.000 -> Transforma em 0.100 x 10^1
    v4 = m10_edge.fl(0.9996)
    print(f"Entrada: 0.9996 | fl(x): {v4} (Esperado: 1.0)")
    assert v4 == Decimal('1'), "Erro na renormalização pós-arredondamento"
    
    print("\n" + "=" * 60)
    print(" 🎉 TODOS OS TESTES PASSARAM COM 100% DE SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()