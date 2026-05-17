from machine import (
    FiniteMachine,
    RoundingMode,
    OverflowMachineError
)


def separator(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def show_result(label, value):
    print(f"{label}: {value}")


def main():

    # =====================================================
    # MÁQUINA
    # =====================================================

    machine = FiniteMachine(
        base=10,
        precision=4,
        exponent_min=-5,
        exponent_max=5,
        rounding=RoundingMode.ROUND
    )

    separator("CONFIGURAÇÃO DA MÁQUINA")

    print(machine.info())

    # =====================================================
    # NORMALIZAÇÃO
    # =====================================================

    separator("NORMALIZAÇÃO")

    values = [
        12345.6789,
        0.000012345,
        -9876.54321,
        3.1415926535,
        0.999999,
        99999.999
    ]

    for v in values:

        try:

            fl_value = machine.fl(v)

            print(f"\nOriginal: {v}")
            print(f"Machine : {fl_value}")

            machine.print_machine_number(v)

        except Exception as e:
            print(f"\nValue: {v}")
            print("ERROR:", e)

    # =====================================================
    # ARREDONDAMENTO VS TRUNCAMENTO
    # =====================================================

    separator("ROUND VS TRUNCATE")

    round_machine = FiniteMachine(
        base=10,
        precision=4,
        exponent_min=-10,
        exponent_max=10,
        rounding=RoundingMode.ROUND
    )

    truncate_machine = FiniteMachine(
        base=10,
        precision=4,
        exponent_min=-10,
        exponent_max=10,
        rounding=RoundingMode.TRUNCATE
    )

    test_value = 12.98765

    print("\nOriginal:", test_value)

    print(
        "Rounded :",
        round_machine.fl(test_value)
    )

    print(
        "Truncated:",
        truncate_machine.fl(test_value)
    )

    # =====================================================
    # SOMA
    # =====================================================

    separator("ADIÇÃO")

    a = 1.23456
    b = 9.87654

    result = machine.add(a, b)

    show_result("a", machine.fl(a))
    show_result("b", machine.fl(b))
    show_result("a + b", result)

    # =====================================================
    # SUBTRAÇÃO
    # =====================================================

    separator("SUBTRAÇÃO")

    a = 10.0001
    b = 9.9999

    result = machine.sub(a, b)

    show_result("a", machine.fl(a))
    show_result("b", machine.fl(b))
    show_result("a - b", result)

    # =====================================================
    # MULTIPLICAÇÃO
    # =====================================================

    separator("MULTIPLICAÇÃO")

    a = 123.456
    b = 0.78901

    result = machine.mul(a, b)

    show_result("a", machine.fl(a))
    show_result("b", machine.fl(b))
    show_result("a * b", result)

    # =====================================================
    # DIVISÃO
    # =====================================================

    separator("DIVISÃO")

    a = 10
    b = 3

    result = machine.div(a, b)

    show_result("a", machine.fl(a))
    show_result("b", machine.fl(b))
    show_result("a / b", result)

    # =====================================================
    # CANCELAMENTO NUMÉRICO
    # =====================================================

    separator("CANCELAMENTO NUMÉRICO")

    a = 1234.567
    b = 1234.566

    result = machine.sub(a, b)

    show_result("a", machine.fl(a))
    show_result("b", machine.fl(b))
    show_result("a - b", result)

    # =====================================================
    # UNDERFLOW
    # =====================================================

    separator("UNDERFLOW")

    very_small = 0.000000000001

    result = machine.fl(very_small)

    print("Original :", very_small)
    print("Machine  :", result)

    # =====================================================
    # OVERFLOW
    # =====================================================

    separator("OVERFLOW")

    try:

        huge = 999999999999999

        result = machine.fl(huge)

        print(result)

    except OverflowMachineError as e:

        print("Overflow detected!")
        print(e)

    # =====================================================
    # BASE 2
    # =====================================================

    separator("BASE 2")

    binary_machine = FiniteMachine(
        base=2,
        precision=5,
        exponent_min=-10,
        exponent_max=10,
        rounding=RoundingMode.ROUND
    )

    values = [
        13.625,
        0.1,
        255.75
    ]

    for v in values:

        try:

            print(f"\nOriginal: {v}")

            result = binary_machine.fl(v)

            print(f"Machine : {result}")

            binary_machine.print_machine_number(v)

        except Exception as e:
            print("ERROR:", e)

    # =====================================================
    # TESTE EM CADEIA
    # =====================================================

    separator("PROPAGAÇÃO DE ERRO")

    x = machine.fl(1)

    for i in range(20):

        x = machine.div(x, 3)

        print(f"Iter {i+1:02d}: {x}")

    # =====================================================
    # CONTADORES
    # =====================================================

    separator("ESTATÍSTICAS")

    print(machine.info())


if __name__ == "__main__":
    main()