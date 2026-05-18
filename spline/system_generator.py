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
    for i in range(len(points) - 1):
        if machine:
            hi = machine.sub(points[i + 1].x, points[i].x)
        else:
            hi = points[i + 1].x - points[i].x
        
        if hi == 0:
            raise ValueError("Invalid spline: duplicate x values (h=0)")
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

    # Inicialização da Matriz e Vetor
    A = [[0.0 for _ in range(size)] for _ in range(size)]
    d = [0.0 for _ in range(size)]

    for i in range(size):
        k = i + 1  # Índice correspondente ao ponto interno k
        h_left = h[k - 1]
        h_right = h[k]

        if machine:
            # Diagonal Principal: 2 * (h_left + h_right)
            sum_h = machine.add(h_left, h_right)
            A[i][i] = machine.mul(Decimal("2"), sum_h)

            # Subdiagonal e Superdiagonal
            if i > 0:
                A[i][i - 1] = h_left
            if i < size - 1:
                A[i][i + 1] = h_right

            # Vetor Independente (d_i)
            # 6 * [ (y_{k+1}-y_k)/h_right - (y_k-y_{k-1})/h_left ]
            dy_right = machine.sub(points[k + 1].y, points[k].y)
            slope_right = machine.div(dy_right, h_right)

            dy_left = machine.sub(points[k].y, points[k - 1].y)
            slope_left = machine.div(dy_left, h_left)

            diff_slopes = machine.sub(slope_right, slope_left)
            d[i] = machine.mul(Decimal("6"), diff_slopes)
            
        else:
            # Caso sem máquina (Aritmética ideal)
            A[i][i] = 2 * (h_left + h_right)
            if i > 0: A[i][i - 1] = h_left
            if i < size - 1: A[i][i + 1] = h_right

            d[i] = 6 * ((points[k + 1].y - points[k].y) / h_right - 
                        (points[k].y - points[k - 1].y) / h_left)

    return A, d