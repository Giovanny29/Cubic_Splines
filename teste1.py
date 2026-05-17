from numerical.machine import (
    FiniteMachine,
    RoundingMode
)

from numerical.jacobi import jacobi
from numerical.gauss_seidel import gauss_seidel

from numerical.convergence import (
    is_diagonally_dominant
)


def separator(title):

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_result(name, result):

    print(f"\n{name}")

    print("Solution   :", result["solution"])
    print("Iterations :", result["iterations"])
    print("Converged  :", result["converged"])
    print("Error      :", result["error"])


machine = FiniteMachine(
    base=10,
    precision=6,
    exponent_min=-10,
    exponent_max=10,
    rounding=RoundingMode.ROUND
)

# =========================================================
# EXEMPLO 1
# =========================================================

separator("EXAMPLE 1 - SIMPLE 3x3")

A = [
    [10, 1, 1],
    [2, 10, 1],
    [2, 2, 10]
]

b = [12, 13, 14]

print("Diagonal dominant:")
print(is_diagonally_dominant(A))

jacobi_result = jacobi(
    A,
    b,
    machine
)

gs_result = gauss_seidel(
    A,
    b,
    machine
)

print_result("JACOBI", jacobi_result)
print_result("GAUSS-SEIDEL", gs_result)

# =========================================================
# EXEMPLO 2
# =========================================================

separator("EXAMPLE 2 - 4x4")

A = [
    [10, -1, 2, 0],
    [-1, 11, -1, 3],
    [2, -1, 10, -1],
    [0, 3, -1, 8]
]

b = [6, 25, -11, 15]

print("Diagonal dominant:")
print(is_diagonally_dominant(A))

jacobi_result = jacobi(
    A,
    b,
    machine
)

gs_result = gauss_seidel(
    A,
    b,
    machine
)

print_result("JACOBI", jacobi_result)
print_result("GAUSS-SEIDEL", gs_result)

# =========================================================
# EXEMPLO 3
# =========================================================

separator("EXAMPLE 3 - NON DIAGONALLY DOMINANT")

A = [
    [1, 3],
    [2, 1]
]

b = [5, 5]

print("Diagonal dominant:")
print(is_diagonally_dominant(A))

jacobi_result = jacobi(
    A,
    b,
    machine,
    max_iter=25
)

gs_result = gauss_seidel(
    A,
    b,
    machine,
    max_iter=25
)

print_result("JACOBI", jacobi_result)
print_result("GAUSS-SEIDEL", gs_result)

# =========================================================
# EXEMPLO 4
# =========================================================

separator("EXAMPLE 4 - PRECISION COMPARISON")

A = [
    [10, 1, 1],
    [2, 10, 1],
    [2, 2, 10]
]

b = [12, 13, 14]

low_precision_machine = FiniteMachine(
    base=10,
    precision=2,
    exponent_min=-10,
    exponent_max=10,
    rounding=RoundingMode.ROUND
)

high_precision_machine = FiniteMachine(
    base=10,
    precision=8,
    exponent_min=-10,
    exponent_max=10,
    rounding=RoundingMode.ROUND
)

print("\nLOW PRECISION")

result_low = gauss_seidel(
    A,
    b,
    low_precision_machine
)

print_result("GAUSS-SEIDEL", result_low)

print("\nHIGH PRECISION")

result_high = gauss_seidel(
    A,
    b,
    high_precision_machine
)

print_result("GAUSS-SEIDEL", result_high)

# =========================================================
# EXEMPLO 5
# =========================================================

separator("EXAMPLE 5 - ROUND VS TRUNCATE")

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

A = [
    [4, 1],
    [2, 3]
]

b = [1, 2]

print("\nROUND MACHINE")

round_result = gauss_seidel(
    A,
    b,
    round_machine
)

print_result("GAUSS-SEIDEL", round_result)

print("\nTRUNCATE MACHINE")

truncate_result = gauss_seidel(
    A,
    b,
    truncate_machine
)

print_result("GAUSS-SEIDEL", truncate_result)

# =========================================================
# EXEMPLO 6
# =========================================================

separator("EXAMPLE 6 - LARGE SYSTEM")

A = [
    [15, -1, 0, 0, 2],
    [-1, 14, -1, 0, 0],
    [0, -1, 13, -1, 0],
    [0, 0, -1, 12, -1],
    [2, 0, 0, -1, 11]
]

b = [14, 13, 12, 11, 10]

print("Diagonal dominant:")
print(is_diagonally_dominant(A))

jacobi_result = jacobi(
    A,
    b,
    machine
)

gs_result = gauss_seidel(
    A,
    b,
    machine
)

print_result("JACOBI", jacobi_result)
print_result("GAUSS-SEIDEL", gs_result)

# =========================================================
# EXEMPLO 7
# =========================================================

separator("EXAMPLE 7 - UNDERFLOW EFFECT")

tiny_machine = FiniteMachine(
    base=10,
    precision=4,
    exponent_min=-3,
    exponent_max=3,
    rounding=RoundingMode.ROUND
)

A = [
    [10, 1],
    [1, 10]
]

b = [0.0001, 0.0001]

result = gauss_seidel(
    A,
    b,
    tiny_machine
)

print_result("GAUSS-SEIDEL", result)

print("\nMachine stats:")
print(tiny_machine.info())