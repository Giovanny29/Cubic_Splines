from decimal import (
    Decimal,
    ROUND_HALF_UP,
    ROUND_DOWN,
    getcontext
)

from enum import Enum


class RoundingMode(Enum):
    TRUNCATE = "truncate"
    ROUND = "round"


class OverflowMachineError(Exception):
    pass


class InvalidBaseError(Exception):
    pass


class InvalidPrecisionError(Exception):
    pass


class FiniteMachine:
    """
    Máquina finita F(b, t, k1, k2)

    Representação normalizada:

        ±0.m1m2...mt × b^z

    com:

        1/b <= mantissa < 1
    """

    def __init__(
        self,
        base=10,
        precision=4,
        exponent_min=-10,
        exponent_max=10,
        rounding=RoundingMode.ROUND
    ):

        if base < 2:
            raise InvalidBaseError(
                "Base must be >= 2"
            )

        if precision < 1:
            raise InvalidPrecisionError(
                "Precision must be >= 1"
            )

        self.base = base
        self.precision = precision
        self.exponent_min = exponent_min
        self.exponent_max = exponent_max
        self.rounding = rounding

        self.overflow_count = 0
        self.underflow_count = 0

        # Precisão alta interna
        getcontext().prec = 100

        # =====================================================
        # IMPORTANTE
        # =====================================================
        #
        # A implementação da precisão da mantissa
        # é decimal.
        #
        # Portanto:
        #
        # base != 10 NÃO possui precisão
        # realmente baseada na base escolhida.
        #
        # A normalização funciona para qualquer base,
        # mas a quantização da mantissa é decimal.
        #
        # Para este projeto isso é aceitável,
        # desde que a máquina seja usada em base 10.
        #
        # =====================================================

    # =========================================================
    # UTILITÁRIOS
    # =========================================================

    def _to_decimal(self, value):

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    def _rounding_mode(self):

        if self.rounding == RoundingMode.TRUNCATE:
            return ROUND_DOWN

        return ROUND_HALF_UP

    def _quantizer(self):

        return Decimal(
            "0." + ("0" * (self.precision - 1)) + "1"
        )

    # =========================================================
    # FL
    # =========================================================

    def fl(self, value):
        """
        Floating machine representation.
        """

        return self.normalize(value)

    # =========================================================
    # NORMALIZAÇÃO
    # =========================================================

    def normalize(self, value):
        """
        Converte um número real no número
        representável da máquina.
        """

        x = self._to_decimal(value)

        if x == 0:
            return Decimal(0)

        sign = -1 if x < 0 else 1

        x = abs(x)

        base = Decimal(self.base)

        exponent = 0

        lower_bound = Decimal(1) / base

        # -----------------------------------------------------
        # NORMALIZA
        #
        # 1/b <= x < 1
        # -----------------------------------------------------

        while x >= 1:
            x = x / base
            exponent += 1

        while x < lower_bound:
            x = x * base
            exponent -= 1

        # -----------------------------------------------------
        # OVERFLOW
        # -----------------------------------------------------

        if exponent > self.exponent_max:

            self.overflow_count += 1

            raise OverflowMachineError(
                f"Overflow: exponent {exponent} "
                f"> {self.exponent_max}"
            )

        # -----------------------------------------------------
        # UNDERFLOW
        # -----------------------------------------------------

        if exponent < self.exponent_min:

            self.underflow_count += 1

            return Decimal(0)

        # -----------------------------------------------------
        # QUANTIZAÇÃO
        # -----------------------------------------------------

        x = x.quantize(
            self._quantizer(),
            rounding=self._rounding_mode()
        )

        # -----------------------------------------------------
        # RENORMALIZA
        #
        # Ex:
        # 0.9999 -> 1.000
        # -----------------------------------------------------

        while x >= 1:

            x = x / base
            exponent += 1

        # -----------------------------------------------------
        # OVERFLOW APÓS ROUND
        # -----------------------------------------------------

        if exponent > self.exponent_max:

            self.overflow_count += 1

            raise OverflowMachineError(
                "Overflow after rounding"
            )

        # -----------------------------------------------------
        # RECONSTRÓI
        # -----------------------------------------------------

        result = sign * x * (base ** exponent)

        return result

    # =========================================================
    # REPRESENTAÇÃO
    # =========================================================

    def machine_representation(self, value):

        machine_number = self.normalize(value)

        if machine_number == 0:

            return {
                "sign": 0,
                "mantissa": Decimal(0),
                "exponent": 0
            }

        sign = -1 if machine_number < 0 else 1

        x = abs(machine_number)

        base = Decimal(self.base)

        exponent = 0

        lower_bound = Decimal(1) / base

        while x >= 1:
            x = x / base
            exponent += 1

        while x < lower_bound:
            x = x * base
            exponent -= 1

        return {
            "sign": sign,
            "mantissa": x,
            "exponent": exponent
        }

    # =========================================================
    # OPERAÇÕES
    # =========================================================

    def add(self, a, b):

        a = self.fl(a)
        b = self.fl(b)

        result = a + b

        return self.fl(result)

    def sub(self, a, b):

        a = self.fl(a)
        b = self.fl(b)

        result = a - b

        return self.fl(result)

    def mul(self, a, b):

        a = self.fl(a)
        b = self.fl(b)

        result = a * b

        return self.fl(result)

    def div(self, a, b):

        a = self.fl(a)
        b = self.fl(b)

        if b == 0:
            raise ZeroDivisionError(
                "Division by zero"
            )

        result = a / b

        return self.fl(result)

    def abs(self, x):

        x = self.fl(x)

        return self.fl(abs(x))

    # =========================================================
    # ERRO RELATIVO
    # =========================================================

    def relative_error(self, real, approx):

        real = self._to_decimal(real)
        approx = self._to_decimal(approx)

        if real == 0:
            return Decimal(0)

        return abs(real - approx) / abs(real)

    # =========================================================
    # VALIDAÇÃO
    # =========================================================

    def is_machine_number(self, value):

        try:

            normalized = self.fl(value)

            return normalized == self._to_decimal(value)

        except Exception:
            return False

    # =========================================================
    # VETORES
    # =========================================================

    def vector(self, values):

        return [
            self.fl(v)
            for v in values
        ]

    # =========================================================
    # MATRIZES
    # =========================================================

    def matrix(self, matrix):

        return [
            [self.fl(v) for v in row]
            for row in matrix
        ]

    # =========================================================
    # INFO
    # =========================================================

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

    # =========================================================
    # DEBUG
    # =========================================================

    def print_machine_number(self, value):

        rep = self.machine_representation(value)

        sign = "-" if rep["sign"] < 0 else "+"

        print(
            f"{sign}"
            f"{rep['mantissa']} "
            f"x {self.base}^{rep['exponent']}"
        )
if __name__ == "__main__":

    
    machine = FiniteMachine(
        base=10,
        precision=4,
        exponent_min=-5,
        exponent_max=5,
        rounding=RoundingMode.ROUND
    )

    x = machine.normalize(12345.6789)

    print(x)

    machine.print_machine_number(12345.6789)

    a = machine.normalize(1.23456)
    b = machine.normalize(9.87654)

    print(machine.add(a, b))
    print(machine.mul(a, b))
    print(machine.div(a, b))