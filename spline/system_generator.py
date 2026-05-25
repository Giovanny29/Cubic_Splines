"""
Module: system_generator.py
Description: Generates the tridiagonal linear system for Natural Cubic Splines 
             using finite machine arithmetic.
"""
from decimal import Decimal

def validate_points(points):
    if len(points) < 3:
        raise ValueError("At least 3 points required for cubic spline")
    for i in range(len(points) - 1):
        if points[i].x >= points[i + 1].x:
            raise ValueError("Points must be strictly sorted by x")

def compute_h(points, machine=None):
    h = []
    zero_m = machine.fl(0) if machine else 0.0
    
    for i in range(len(points) - 1):
        if machine:
            # Garante que os pontos de entrada passem pela filtragem da máquina
            px_next = machine.fl(points[i + 1].x)
            px_curr = machine.fl(points[i].x)
            hi = machine.sub(px_next, px_curr)
        else:
            hi = points[i + 1].x - points[i].x
        
        if hi == zero_m:
            raise ValueError("Invalid spline: duplicate or geometrically indistinguishable x values (h=0) for this machine configuration.")
        h.append(hi)
    return h

def generate_natural_spline_system(points, machine=None):
    """
    Gera o sistema tridiagonal A*g = d para as segundas derivadas.
    Reduz o sistema para (n-1) equações considerando g0 = gn = 0.
    """
    validate_points(points)
    n = len(points) - 1
    h = compute_h(points, machine)
    size = n - 1

    # Inicialização coerente com o tipo numérico do ambiente
    if machine:
        zero_val = machine.fl(0)
        A = [[zero_val for _ in range(size)] for _ in range(size)]
        d = [zero_val for _ in range(size)]
    else:
        A = [[0.0 for _ in range(size)] for _ in range(size)]
        d = [0.0 for _ in range(size)]

    for i in range(size):
        k = i + 1  # Índice correspondente ao ponto interno k
        h_left = h[k - 1]
        h_right = h[k]

        if machine:
            # Garantia de que os valores de Y estão na aritmética da máquina
            py_next = machine.fl(points[k + 1].y)
            py_curr = machine.fl(points[k].y)
            py_prev = machine.fl(points[k - 1].y)

            # Diagonal Principal: 2 * (h_left + h_right)
            sum_h = machine.add(h_left, h_right)
            A[i][i] = machine.mul(machine.fl(2), sum_h)

            # Subdiagonal e Superdiagonal
            if i > 0:
                A[i][i - 1] = h_left
            if i < size - 1:
                A[i][i + 1] = h_right

            # Vetor Independente (d_i)
            # 6 * [ (y_{k+1}-y_k)/h_right - (y_k-y_{k-1})/h_left ]
            dy_right = machine.sub(py_next, py_curr)
            slope_right = machine.div(dy_right, h_right)

            dy_left = machine.sub(py_curr, py_prev)
            slope_left = machine.div(dy_left, h_left)

            diff_slopes = machine.sub(slope_right, slope_left)
            d[i] = machine.mul(machine.fl(6), diff_slopes)
            
        else:
            # Caso sem máquina (Aritmética ideal)
            A[i][i] = 2 * (h_left + h_right)
            if i > 0: A[i][i - 1] = h_left
            if i < size - 1: A[i][i + 1] = h_right

            d[i] = 6 * ((points[k + 1].y - points[k].y) / h_right - 
                        (points[k].y - points[k - 1].y) / h_left)

    return A, d