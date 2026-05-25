"""
Module: spline_evaluator.py
Description: Evaluates points on the built spline, finding the correct segment
             efficiently using binary search (bisect).
"""
import bisect

class SplineEvaluator:
    def __init__(self, segments):
        self.segments = segments
        # Guarda os pontos de quebra (X0 de cada segmento + o X1 do último) para a busca binária
        self.breakpoints = []
        if segments:
            self.breakpoints = [float(seg.x0) for seg in segments]
            self.breakpoints.append(float(segments[-1].x1))

    def evaluate(self, x):
        """
        Localiza eficientemente o segmento que contém 'x' via busca binária
        e retorna o valor interpolado.
        """
        if not self.segments:
            return 0.0
            
        x_val = float(x)
        
        # Tratamento de Extrapolação (Clamping nas bordas)
        if x_val <= self.breakpoints[0]:
            return self.segments[0].evaluate(x)
        if x_val >= self.breakpoints[-1]:
            return self.segments[-1].evaluate(x)

        # Busca Binária: Encontra o índice do intervalo onde o x_val se encaixa
        # bisect_right retorna onde o elemento seria inserido, o que casa perfeitamente com idx - 1
        idx = bisect.bisect_right(self.breakpoints, x_val) - 1
        
        # Ajuste de segurança para o limite superior exato
        if idx >= len(self.segments):
            idx = len(self.segments) - 1
            
        return self.segments[idx].evaluate(x)

    def evaluate_list(self, x_list):
        """Avalia uma lista inteira de pontos (útil para renderização rápida de gráficos)"""
        return [self.evaluate(x) for x in x_list]