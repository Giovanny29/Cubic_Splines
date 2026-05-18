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

    Permite simular com precisão o comportamento de sistemas numéricos com
    mantissa limitada, capturando erros de arredondamento, truncamento,
    cancellation, sobrefluxo (overflow) e subfluxo (underflow).
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

        # Define uma precisão interna alta no módulo decimal para evitar que
        # o interpretador Python introduza ruídos nos cálculos intermediários.
        getcontext().prec = 100

    # =====================================================
    # CONVERSÃO INTERNA
    # =====================================================

    def _to_decimal(self, value):
        """
        Converte com segurança qualquer entrada numérica para o tipo Decimal do Python.

        Entrada:
            value (int/float/str/Decimal): O valor que será convertido.
        Saída:
            Decimal: O valor perfeitamente tipado como Decimal.
        """
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    # =====================================================
    # FUNÇÃO PRINCIPAL: FL (floating machine)
    # =====================================================

    def fl(self, value):
        """
        Aplica o operador fl(x), mapeando um número real contínuo para
        o conjunto finito de valores representáveis por esta máquina.

        Entrada:
            value (int/float/str/Decimal): O valor numérico real de entrada.
        Saída:
            Decimal: O número representado e limitado sob as regras da máquina.
        """
        return self.normalize(value)

    # =====================================================
    # NORMALIZAÇÃO E QUANTIZAÇÃO
    # =====================================================

    def normalize(self, value):
        """
        Realiza a normalização do número na forma ±0.m1m2...mt * b^z, aplica
        a limitação de tamanho da mantissa (t), trata underflow/overflow e
        retorna o valor computado final.

        Entrada:
            value (int/float/str/Decimal): O valor bruto a ser processado.
        Saída:
            Decimal: O número final estabilizado e normalizado pela máquina.
        """
        x = self._to_decimal(value)

        if x == 0:
            return Decimal(0)

        sign = -1 if x < 0 else 1
        x = abs(x)

        base = Decimal(self.base)
        exponent = 0
        lower_bound = Decimal(1) / base

        # -------------------------------------------------
        # 1. Ajuste de Escala (Trazer mantissa para [1/b, 1) )
        # -------------------------------------------------
        while x >= 1:
            x /= base
            exponent += 1

        while x < lower_bound:
            x *= base
            exponent -= 1

        # -------------------------------------------------
        # 2. Verificação Prévia de Extremos (Overflow / Underflow)
        # -------------------------------------------------
        if exponent > self.exponent_max:
            self.overflow_count += 1
            raise OverflowMachineError(f"Overflow: exponent {exponent} > {self.exponent_max}")

        if exponent < self.exponent_min:
            self.underflow_count += 1
            return Decimal(0)

        # -------------------------------------------------
        # 3. Quantização da Mantissa (Uso da base genérica b^-t)
        # -------------------------------------------------
        # Multiplicamos por b^t para transformar a parte fracionária relevante em inteiro
        shift = base ** self.precision
        x_shifted = x * shift

        if self.rounding == RoundingMode.TRUNCATE:
            # Truncamento puro (descarta o que sobrou)
            x_shifted = x_shifted.quantize(Decimal('1'), rounding=ROUND_DOWN)
        else:
            # Arredondamento padrão para o mais próximo
            x_shifted = x_shifted.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

        # Devolvemos a mantissa para a escala original [1/b, 1)
        x = x_shifted / shift

        # -------------------------------------------------
        # 4. Renormalização (Caso o arredondamento empurre a mantissa para 1.0)
        # -------------------------------------------------
        while x >= 1:
            x /= base
            exponent += 1

        # -------------------------------------------------
        # 5. Validação Pós-Arredondamento
        # -------------------------------------------------
        if exponent > self.exponent_max:
            self.overflow_count += 1
            raise OverflowMachineError("Overflow after rounding")

        if exponent < self.exponent_min:
            self.underflow_count += 1
            return Decimal(0)

        return sign * x * (base ** exponent)

    # =====================================================
    # REPRESENTAÇÃO INTERNA
    # =====================================================

    def machine_representation(self, value):
        """
        Extrai de forma explícita os componentes do número armazenado na máquina
        para relatórios, depuração visual ou logs do sistema.

        Entrada:
            value (int/float/str/Decimal): O valor que deseja analisar.
        Saída:
            dict: Um dicionário contendo:
                - "sign" (int): 1 para positivo, -1 para negativo, 0 para zero.
                - "mantissa" (Decimal): O valor fracionário normalizado.
                - "exponent" (int): O expoente z associado à base.
        """
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
        """
        Soma dois números simulando a aritmética interna com arredondamento fl(a + b).

        Entrada:
            a, b (valores numéricos): Operandos da soma.
        Saída:
            Decimal: Resultado quantizado pela máquina.
        """
        return self.fl(self._to_decimal(a) + self._to_decimal(b))

    def sub(self, a, b):
        """
        Subtrai dois números simulando a aritmética interna com arredondamento fl(a - b).

        Entrada:
            a, b (valores numéricos): Operandos da subtração (a - b).
        Saída:
            Decimal: Resultado quantizado pela máquina.
        """
        return self.fl(self._to_decimal(a) - self._to_decimal(b))

    def mul(self, a, b):
        """
        Multiplica dois números simulando a aritmética interna com arredondamento fl(a * b).

        Entrada:
            a, b (valores numéricos): Operandos da multiplicação.
        Saída:
            Decimal: Resultado quantizado pela máquina.
        """
        return self.fl(self._to_decimal(a) * self._to_decimal(b))

    def div(self, a, b):
        """
        Divide dois números simulando a aritmética interna com arredondamento fl(a / b).

        Entrada:
            a, b (valores numéricos): Dividendo (a) e Divisor (b).
        Saída:
            Decimal: Resultado quantizado pela máquina.
        """
        if self._to_decimal(b) == 0:
            raise ZeroDivisionError("Division by zero inside FiniteMachine.")
        return self.fl(self._to_decimal(a) / self._to_decimal(b))

    def abs(self, x):
        """
        Calculo do valor absoluto estabilizado pelas regras da máquina fl(|x|).

        Entrada:
            x (valores numéricos): Número que terá o módulo extraído.
        Saída:
            Decimal: Módulo quantizado.
        """
        return self.fl(abs(self._to_decimal(x)))

    # =====================================================
    # CONVERSÃO DE ESTRUTURAS DE DADOS
    # =====================================================

    def vector(self, values):
        """
        Converte uma lista nativa do Python em um vetor onde todos os elementos
        passaram pelo truncamento/arredondamento da máquina finita.

        Entrada:
            values (list): Lista de floats/ints originais.
        Saída:
            list[Decimal]: Lista modificada contendo os Decimais ajustados.
        """
        return [self.fl(v) for v in values]

    def matrix(self, matrix):
        """
        Converte uma matriz bidimensional (lista de listas) em uma estrutura
        onde cada célula individual respeita os limites da máquina finita.

        Entrada:
            matrix (list[list]): Matriz original de dados reais.
        Saída:
            list[list[Decimal]]: Matriz processada com dados quantizados.
        """
        return [[self.fl(v) for v in row] for row in matrix]

    # =====================================================
    # MÉTRICAS E DEPURAÇÃO
    # =====================================================

    def relative_error(self, real, approx):
        """
        Calcula o erro relativo exato entre um valor de referência real e o valor aproximado.

        Entrada:
            real (valores numéricos): Valor real analítico de controle.
            approx (valores numéricos): Valor aproximado obtido pela máquina.
        Saída:
            Decimal: Erro relativo adimensional (|real - approx| / |real|).
        """
        real = self._to_decimal(real)
        approx = self._to_decimal(approx)

        if real == 0:
            return Decimal(0)

        return abs(real - approx) / abs(real)

    def info(self):
        """
        Retorna o estado atual das variáveis de configuração e contadores da máquina.

        Saída:
            dict: Dicionário completo de telemetria da máquina virtual.
        """
        return {
            "base": self.base,
            "precision": self.precision,
            "exponent_min": self.exponent_min,
            "exponent_max": self.exponent_max,
            "rounding": self.rounding.value,
            "overflow_count": self.overflow_count,
            "underflow_count": self.underflow_count
        }

    def print_machine_number(self, value):
        """
        Exibe na tela a formatação científica exata com base na representação de máquina.

        Entrada:
            value (valores numéricos): O dado que será renderizado no terminal.
        """
        rep = self.machine_representation(value)
        sign = "-" if rep["sign"] < 0 else "+"
        print(f"{sign}{rep['mantissa']} x {self.base}^{rep['exponent']}")