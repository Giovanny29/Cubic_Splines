from decimal import (
    Decimal,
    ROUND_HALF_UP,
    ROUND_DOWN,
    getcontext
)
from enum import Enum

# =========================================================
# MODOS DE ARREDONDAMENTO
# =========================================================

class RoundingMode(Enum):
    TRUNCATE = "truncate"
    ROUND = "round"


# =========================================================
# EXCEÇÕES DA MÁQUINA
# =========================================================

class OverflowMachineError(Exception):
    pass


class InvalidBaseError(Exception):
    pass


class InvalidPrecisionError(Exception):
    pass


# =========================================================
# MÁQUINA FINITA F(b, t, k1, k2)
# =========================================================

class FiniteMachine:
    """
    Modelo de máquina finita que simula aritmética de ponto flutuante:
        ±0.m1m2...mt × b^z

    Mantém o armazenamento interno em Decimal (base 10), mas restringe os valores
    e propaga os erros como se estivessem na base (b) com (t) dígitos de mantissa.
    """

    def __init__(
        self,
        base=10,
        precision=4,
        exponent_min=-10,
        exponent_max=10,
        rounding=RoundingMode.ROUND
    ):
        """
        Inicializa a máquina finita com os parâmetros estruturais do sistema numérico.

        Entrada:
            base (int): Base do sistema numérico (b >= 2). Padrão: 10.
            precision (int): Quantidade de dígitos da mantissa (t >= 1). Padrão: 4.
            exponent_min (int): Limite inferior do expoente (k1). Padrão: -10.
            exponent_max (int): Limite superior do expoente (k2). Padrão: 10.
            rounding (RoundingMode): Modo de corte (ROUND ou TRUNCATE). Padrão: ROUND.
        """
        if base < 2:
            raise InvalidBaseError("Base must be >= 2")

        if precision < 1:
            raise InvalidPrecisionError("Precision must be >= 1")

        self.base = base
        self.precision = precision
        self.exponent_min = exponent_min
        self.exponent_max = exponent_max
        self.rounding = rounding

        self.overflow_count = 0
        self.underflow_count = 0

        # Define uma precisão interna altíssima para o Python não gerar ruído próprio
        getcontext().prec = 100

    def _to_decimal(self, value):
        """Converte entradas com segurança para Decimal."""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def fl(self, value):
        """Operador fl(x) da máquina."""
        return self.normalize(value)

    def normalize(self, value):
        """
        Normaliza, quantiza na base b com t dígitos, trata overflow/underflow
        e retorna o valor resultante mapeado de volta em Decimal (base 10).
        """
        x = self._to_decimal(value)

        if x == 0:
            return Decimal(0)

        sign = -1 if x < 0 else 1
        x = abs(x)

        base = Decimal(self.base)
        exponent = 0
        lower_bound = Decimal(1) / base

        # 1. Traz a escala para o intervalo de representação [1/b, 1)
        while x >= 1:
            x /= base
            exponent += 1

        while x < lower_bound:
            x *= base
            exponent -= 1

        # 2. Verificação prévia de limites de expoente
        if exponent > self.exponent_max:
            self.overflow_count += 1
            raise OverflowMachineError(f"Overflow: exponent {exponent} > {self.exponent_max}")

        if exponent < self.exponent_min:
            self.underflow_count += 1
            return Decimal(0)

        # 3. Quantização baseada nos t dígitos da base b
        shift = base ** self.precision
        x_shifted = x * shift

        if self.rounding == RoundingMode.TRUNCATE:
            x_shifted = x_shifted.quantize(Decimal('1'), rounding=ROUND_DOWN)
        else:
            x_shifted = x_shifted.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        x = x_shifted / shift

        # 4. Renormalização caso o arredondamento jogue a mantissa para 1.0
        while x >= 1:
            x /= base
            exponent += 1

        # 5. Verificação final pós-arredondamento
        if exponent > self.exponent_max:
            self.overflow_count += 1
            raise OverflowMachineError("Overflow after rounding")

        if exponent < self.exponent_min:
            self.underflow_count += 1
            return Decimal(0)

        # Devolve o valor convertido de volta para a nossa escala decimal de trabalho
        return sign * x * (base ** exponent)

    def machine_representation(self, value):
        """Retorna o sinal, a mantissa e o expoente normalizados na base da máquina."""
        m = self.normalize(value)

        if m == 0:
            return {"sign": 0, "mantissa": Decimal(0), "exponent": 0}

        sign = -1 if m < 0 else 1
        x = abs(m)

        base = Decimal(self.base)
        exponent = 0
        lower_bound = Decimal(1) / base

        while x >= 1:
            x /= base
            exponent += 1

        while x < lower_bound:
            x *= base
            exponent -= 1

        return {
            "sign": sign,
            "mantissa": x,
            "exponent": exponent
        }

    # =====================================================
    # OPERAÇÕES ARITMÉTICAS DA MÁQUINA
    # =====================================================

    def add(self, a, b):
        return self.fl(self._to_decimal(a) + self._to_decimal(b))

    def sub(self, a, b):
        return self.fl(self._to_decimal(a) - self._to_decimal(b))

    def mul(self, a, b):
        return self.fl(self._to_decimal(a) * self._to_decimal(b))

    def div(self, a, b):
        if self._to_decimal(b) == 0:
            raise ZeroDivisionError("Division by zero inside FiniteMachine.")
        return self.fl(self._to_decimal(a) / self._to_decimal(b))

    def abs(self, x):
        return self.fl(abs(self._to_decimal(x)))

    def vector(self, values):
        return [self.fl(v) for v in values]

    def matrix(self, matrix):
        return [[self.fl(v) for v in row] for row in matrix]

    def relative_error(self, real, approx):
        real = self._to_decimal(real)
        approx = self._to_decimal(approx)
        if real == 0:
            return Decimal(0)
        return abs(real - approx) / abs(real)

    def info(self):
        return {
            "base": self.base,
            "precision": self.precision,
            "exponent_min": self.exponent_min,
            "exponent_max": self.exponent_max,
            "rounding": self.rounding.value,
            "overflow_count": self.overflow_count,
            "underflow_count": self.underflow_count
        }

    # =====================================================
    # CONVERSÃO VISUAL DE DIGITOS PARA EXIBIÇÃO
    # =====================================================

    def _convert_mantissa_to_base_digits(self, mantissa_decimal):
        """Converte a mantissa decimal interna para uma string com os dígitos reais da base b."""
        digits = []
        rem = mantissa_decimal
        hex_chars = "0123456789ABCDEF"
        
        for _ in range(self.precision):
            rem *= self.base
            digit_value = int(rem)
            
            if self.base <= 16:
                digits.append(hex_chars[digit_value])
            else:
                digits.append(f"({digit_value})")
                
            rem -= digit_value
            
        return "".join(digits)

    def print_machine_number(self, value):
        """Exibe o número com os dígitos reais correspondentes à base."""
        rep = self.machine_representation(value)
        if rep["sign"] == 0:
          # Certo (aspas simples dentro da f-string)
            print(f"+0.{'0' * self.precision} x {self.base}^0")
            return

        sign = "-" if rep["sign"] < 0 else "+"
        digits_string = self._convert_mantissa_to_base_digits(rep["mantissa"])
        print(f"{sign}0.{digits_string} x {self.base}^{rep['exponent']}")