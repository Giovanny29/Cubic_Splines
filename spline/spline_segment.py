"""
Module: spline_segment.py
Description: Represents a single cubic polynomial segment between two points
             using the second derivative (Moments) formulation.
"""
from decimal import Decimal

class SplineSegment:
    def __init__(self, x0, x1, M0, M1, y0, y1, machine=None):
        self.machine = machine
        
        # Se houver máquina, os coeficientes devem passar pelo filtro de ponto flutuante dela imediatamente
        if machine:
            self.x0 = machine.fl(x0)
            self.x1 = machine.fl(x1)
            self.M0 = machine.fl(M0)
            self.M1 = machine.fl(M1)
            self.y0 = machine.fl(y0)
            self.y1 = machine.fl(y1)
            self.h = machine.sub(self.x1, self.x0)
        else:
            self.x0 = Decimal(str(x0))
            self.x1 = Decimal(str(x1))
            self.M0 = Decimal(str(M0))
            self.M1 = Decimal(str(M1))
            self.y0 = Decimal(str(y0))
            self.y1 = Decimal(str(y1))
            self.h = self.x1 - self.x0

        # Validação do intervalo usando o zero correspondente ao ambiente
        zero_val = machine.fl(0) if machine else Decimal("0")
        if self.h == zero_val:
            raise ValueError("Invalid spline segment: x0 == x1 (interval length is zero)")

    def evaluate(self, x):
        m = self.machine

        if not m:
            # Fallback para aritmética ideal se nenhuma máquina for passada
            x_dec = Decimal(str(x))
            term1 = (float(self.M0) * ((float(self.x1) - float(x_dec)) ** 3)) / (6 * float(self.h))
            term2 = (float(self.M1) * ((float(x_dec) - float(self.x0)) ** 3)) / (6 * float(self.h))
            term3 = (float(self.y0) - (float(self.M0) * (float(self.h)**2)) / 6) * ((float(self.x1) - float(x_dec)) / float(self.h))
            term4 = (float(self.y1) - (float(self.M1) * (float(self.h)**2)) / 6) * ((float(x_dec) - float(self.x0)) / float(self.h))
            return term1 + term2 + term3 + term4

        # --- ARITMÉTICA DE MÁQUINA FINITA (BLINDADA) ---
        x_m = m.fl(x)
        six = m.fl(6)
        h2 = m.mul(self.h, self.h)
        h_six = m.mul(six, self.h)

        # Pré-calculo dos fatores de divisão para mitigar amplificação de erro no numerador
        factor_M0 = m.div(self.M0, h_six)
        factor_M1 = m.div(self.M1, h_six)

        # Termo 1: (M0 / 6h) * (x1 - x)^3
        dx1 = m.sub(self.x1, x_m)
        dx1_3 = m.mul(m.mul(dx1, dx1), dx1)
        term1 = m.mul(factor_M0, dx1_3)

        # Termo 2: (M1 / 6h) * (x - x0)^3
        dx0 = m.sub(x_m, self.x0)
        dx0_3 = m.mul(m.mul(dx0, dx0), dx0)
        term2 = m.mul(factor_M1, dx0_3)

        # Termo 3: (y0 - M0*h^2/6) * (x1 - x)/h
        m0_h2_6 = m.div(m.mul(self.M0, h2), six)
        base3 = m.sub(self.y0, m0_h2_6)
        ratio3 = m.div(dx1, self.h)
        term3 = m.mul(base3, ratio3)

        # Termo 4: (y1 - M1*h^2/6) * (x - x0)/h
        m1_h2_6 = m.div(m.mul(self.M1, h2), six)
        base4 = m.sub(self.y1, m1_h2_6)
        ratio4 = m.div(dx0, self.h)
        term4 = m.mul(base4, ratio4)

        # Soma acumulada estritamente na ordem da esquerda para a direita
        res = m.add(term1, term2)
        res = m.add(res, term3)
        res = m.add(res, term4)

        return float(res)

    def contains(self, x):
        return float(self.x0) <= float(x) <= float(self.x1)

    def __repr__(self):
        return f"SplineSegment(x0={float(self.x0)}, x1={float(self.x1)})"