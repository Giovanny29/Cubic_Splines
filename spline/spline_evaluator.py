"""
Module: spline_evaluator.py
Description: Evaluates points on the built spline, finding the correct segment.
"""

class SplineEvaluator:
    def __init__(self, segments):
        self.segments = segments

    def evaluate(self, x):
        """
        Localiza o segmento que contém 'x' e retorna o valor interpolado.
        """
        if not self.segments:
            return 0.0
            
        # Para valores fora do intervalo (extrapolação), usamos os limites
        if x <= self.segments[0].x0:
            return self.segments[0].evaluate(x)
        if x >= self.segments[-1].x1:
            return self.segments[-1].evaluate(x)

        # Busca o segmento correto
        for segment in self.segments:
            if segment.contains(x):
                return segment.evaluate(x)
        
        return 0.0

    def evaluate_list(self, x_list):
        """Avalia uma lista inteira de pontos (útil para o gráfico)"""
        return [self.evaluate(x) for x in x_list]