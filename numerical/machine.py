from decimal import (
    Decimal,
    ROUND_DOWN,
    getcontext
)
from enum import Enum

# =========================================================
# MODOS DE ARREDONDAMENTO
# =========================================================

class RoundingMode(Enum):
    """
    Enumeração para os modos de tratamento da mantissa.
    TRUNCATE: Corta os dígitos excedentes (Truncamento clássico).
    ROUND: Arredondamento padrão por proximidade (Universal para qualquer base).
    """
    TRUNCATE = "truncate"
    ROUND = "round"


# =========================================================
# EXCEÇÕES DA MÁQUINA
# =========================================================

class OverflowMachineError(Exception):
    """Lançada quando o expoente supera o limite superior (k2) da máquina."""
    pass


class InvalidBaseError(Exception):
    """Lançada quando a base numérica definida é inválida (b < 2)."""
    pass


class InvalidPrecisionError(Exception):
    """Lançada quando a precisão da mantissa é inválida (t < 1)."""
    pass


# =========================================================
# MÁQUINA FINITA F(b, t, k1, k2)
# =========================================================

class FiniteMachine:
    """
    Modelo de máquina finita que simula aritmética de ponto flutuante:
        ±0.m1m2...mt × b^z

    Mantém o armazenamento interno em Decimal (base 10) com altíssima precisão
    para evitar ruídos do interpretador Python, mas restringe os valores, corta
    a mantissa e propaga os erros estritamente nas regras da base (b) com (t)
    dígitos de precisão informados pelo usuário.
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

        Parâmetros:
            base (int): Base do sistema numérico (b >= 2). Padrão: 10.
            precision (int): Quantidade de dígitos da mantissa (t >= 1). Padrão: 4.
            exponent_min (int): Limite inferior do expoente (k1). Padrão: -10.
            exponent_max (int): Limite superior do expoente (k2). Padrão: 10.
            rounding (RoundingMode): Modo de corte (ROUND ou TRUNCATE). Padrão: ROUND.
        """
        if base < 2:
            raise InvalidBaseError("A base do sistema numérico deve ser >= 2.")

        if precision < 1:
            raise InvalidPrecisionError("A precisão da mantissa (t) deve ser >= 1.")

        self.base = base
        self.precision = precision
        self.exponent_min = exponent_min
        self.exponent_max = exponent_max
        self.rounding = rounding

        # Contadores de falhas numéricas para relatórios de estabilidade
        self.overflow_count = 0
        self.underflow_count = 0

        # Define uma precisão interna altíssima para o Python não gerar ruído próprio
        getcontext().prec = 100

    def _to_decimal(self, value):
        """Converte entradas numéricas com segurança para o tipo Decimal interno."""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def fl(self, value):
        """
        Operador fl(x) da máquina.
        Aplica a modelagem de ponto flutuante limitado sobre o valor real de entrada.
        """
        return self.normalize(value)

    def normalize(self, value):
        """
        Normaliza, quantiza na base b com t dígitos utilizando aritmética rigorosa,
        trata overflow/underflow e retorna o valor resultante mapeado em Decimal.
        """
        x = self._to_decimal(value)

        if x == 0:
            return Decimal(0)

        sign = -1 if x < 0 else 1
        x = abs(x)

        base = Decimal(self.base)
        exponent = 0
        lower_bound = Decimal(1) / base

        # 1. Escalonamento: Traz o valor para o intervalo padrão de representação [1/b, 1)
        while x >= 1:
            x /= base
            exponent += 1

        while x < lower_bound:
            x *= base
            exponent -= 1

        # 2. Verificação prévia de segurança para os limites de expoente
        if exponent > self.exponent_max:
            self.overflow_count += 1
            raise OverflowMachineError(f"Overflow preemptivo: expoente {exponent} > {self.exponent_max}")

        if exponent < self.exponent_min:
            self.underflow_count += 1
            return Decimal(0)

        # 3. Quantização baseada nos t dígitos da base b (Correção Universal Multibase)
        shift = base ** self.precision
        x_shifted = x * shift

        if self.rounding == RoundingMode.TRUNCATE:
            # Elimina completamente a parte fracionária na escala deslocada
            x_shifted = x_shifted.quantize(Decimal('1'), rounding=ROUND_DOWN)
        else:
            # Algoritmo de arredondamento universal: Soma metade da unidade elementar (0.5) 
            # na escala deslocada e aplica o truncamento (ROUND_DOWN). 
            # Funciona perfeitamente e sem desvios para qualquer base (2, 10, 16, etc.)
            x_shifted = (x_shifted + Decimal('0.5')).quantize(Decimal('1'), rounding=ROUND_DOWN)

        x = x_shifted / shift

        # 4. Renormalização: Caso o arredondamento empurre a mantissa para 1.0 (Ex: 0.9999 -> 1.0000)
        while x >= 1:
            x /= base
            exponent += 1

        # 5. Verificação final pós-arredondamento contra estouros de limite
        if exponent > self.exponent_max:
            self.overflow_count += 1
            raise OverflowMachineError("Overflow disparado após ajuste de arredondamento.")

        if exponent < self.exponent_min:
            self.underflow_count += 1
            return Decimal(0)

        # Retorna o valor de volta para a escala decimal do fluxo de execução do programa
        return sign * x * (base ** exponent)

    def machine_representation(self, value):
        """Retorna o sinal, a mantissa isolada e o expoente representados na base b."""
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
    # OPERAÇÕES ARITMÉTICAS ELEMENTARES DA MÁQUINA
    # =====================================================

    def add(self, a, b):
        """Soma aritmética limitada: fl(a + b)"""
        return self.fl(self._to_decimal(a) + self._to_decimal(b))

    def sub(self, a, b):
        """Subtração aritmética limitada: fl(a - b)"""
        return self.fl(self._to_decimal(a) - self._to_decimal(b))

    def mul(self, a, b):
        """Multiplicação aritmética limitada: fl(a * b)"""
        return self.fl(self._to_decimal(a) * self._to_decimal(b))

    def div(self, a, b):
        """Divisão aritmética limitada: fl(a / b)"""
        if self._to_decimal(b) == 0:
            raise ZeroDivisionError("Divisão por zero interceptada dentro da ULA da FiniteMachine.")
        return self.fl(self._to_decimal(a) / self._to_decimal(b))

    def abs(self, x):
        """Valor absoluto limitado: fl(|x|)"""
        return self.fl(abs(self._to_decimal(x)))

    def vector(self, values):
        """Converte e quantiza um vetor unidimensional inteiro nas regras da máquina."""
        return [self.fl(v) for v in values]

    def matrix(self, matrix):
        """Converte e quantiza uma matriz bidimensional inteira nas regras da máquina."""
        return [[self.fl(v) for v in row] for row in matrix]

    def relative_error(self, real, approx):
        """Calcula o erro relativo exato entre o valor real e a aproximação calculada."""
        real = self._to_decimal(real)
        approx = self._to_decimal(approx)
        if real == 0:
            return Decimal(0)
        return abs(real - approx) / abs(real)

    def info(self):
        """Retorna as configurações estruturais e estatísticas de falha da máquina."""
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
    # CONVERSÃO VISUAL DE DÍGITOS PARA EXIBIÇÃO
    # =====================================================

    def _convert_mantissa_to_base_digits(self, mantissa_decimal):
        """Converte a mantissa decimal interna para representação em string na base b."""
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
        """Exibe no terminal o número formatado com os dígitos reais correspondentes à base."""
        rep = self.machine_representation(value)
        if rep["sign"] == 0:
            print(f"+0.{'0' * self.precision} x {self.base}^0")
            return

        sign = "-" if rep["sign"] < 0 else "+"
        digits_string = self._convert_mantissa_to_base_digits(rep["mantissa"])
        print(f"{sign}0.{digits_string} x {self.base}^{rep['exponent']}")