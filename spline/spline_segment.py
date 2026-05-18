"""
Module: spline_segment.py
Description: Represents a single cubic polynomial segment between two points
             using the second derivative (Moments) formulation.
"""
from decimal import Decimal

class SplineSegment:
    def __init__(self, x0, x1, M0, M1, y0, y1, machine=None):
        self.machine = machine
        
        # Guardamos os valores como Decimals para a máquina, mas mantemos floats para compatibilidade
        self.x0 = Decimal(str(x0))
        self.x1 = Decimal(str(x1))
        self.M0 = Decimal(str(M0))
        self.M1 = Decimal(str(M1))
        self.y0 = Decimal(str(y0))
        self.y1 = Decimal(str(y1))

        if machine:
            self.h = machine.sub(self.x1, self.x0)
        else:
            self.h = self.x1 - self.x0

        if self.h == 0:
            raise ValueError("Invalid spline segment: x0 == x1")

    def evaluate(self, x):
        x = Decimal(str(x))
        h = self.h
        m = self.machine

        if not m:
            # Fallback para aritmética ideal se nenhuma máquina for passada
            term1 = (float(self.M0) * ((float(self.x1) - float(x)) ** 3)) / (6 * float(h))
            term2 = (float(self.M1) * ((float(x) - float(self.x0)) ** 3)) / (6 * float(h))
            term3 = (float(self.y0) - (float(self.M0) * (float(h)**2)) / 6) * ((float(self.x1) - float(x)) / float(h))
            term4 = (float(self.y1) - (float(self.M1) * (float(h)**2)) / 6) * ((float(x) - float(self.x0)) / float(h))
            return term1 + term2 + term3 + term4

        # --- ARITMÉTICA DE MÁQUINA FINITA ---
        # Componentes comuns
        six = Decimal("6")
        h2 = m.mul(h, h)
        h_six = m.mul(six, h)

        # Termo 1: M0 * (x1 - x)^3 / (6*h)
        dx1 = m.sub(self.x1, x)
        dx1_3 = m.mul(m.mul(dx1, dx1), dx1)
        term1 = m.div(m.mul(self.M0, dx1_3), h_six)

        # Termo 2: M1 * (x - x0)^3 / (6*h)
        dx0 = m.sub(x, self.x0)
        dx0_3 = m.mul(m.mul(dx0, dx0), dx0)
        term2 = m.div(m.mul(self.M1, dx0_3), h_six)

        # Termo 3: (y0 - M0*h^2/6) * (x1 - x)/h
        m0_h2_6 = m.div(m.mul(self.M0, h2), six)
        base3 = m.sub(self.y0, m0_h2_6)
        ratio3 = m.div(dx1, h)
        term3 = m.mul(base3, ratio3)

        # Termo 4: (y1 - M1*h^2/6) * (x - x0)/h
        m1_h2_6 = m.div(m.mul(self.M1, h2), six)
        base4 = m.sub(self.y1, m1_h2_6)
        ratio4 = m.div(dx0, h)
        term4 = m.mul(base4, ratio4)

        # Soma Final: fl(fl(fl(t1 + t2) + t3) + t4)
        res = m.add(term1, term2)
        res = m.add(res, term3)
        res = m.add(res, term4)

        return float(res)

    def contains(self, x):
        return float(self.x0) <= float(x) <= float(self.x1)

    def __repr__(self):
        return f"SplineSegment(x0={float(self.x0)}, x1={float(self.x1)})"