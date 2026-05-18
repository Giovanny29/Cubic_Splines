from decimal import Decimal


def infinity_norm(vector, machine=None):

    if vector is None or len(vector) == 0:
        return 0

    # =====================================================
    # CASO SEM MÁQUINA (referência ideal)
    # =====================================================

    if machine is None:
        return max(abs(float(x)) for x in vector)

    # =====================================================
    # CASO COM MÁQUINA FINITA
    # =====================================================

    max_value = Decimal(0)

    for x in vector:

        try:
            val = machine.abs(x)

            # garante compatibilidade
            if isinstance(val, Decimal):
                val = abs(val)
            else:
                val = Decimal(str(abs(val)))

        except Exception:
            # se a máquina explodir, trata como valor grande
            val = Decimal("1e100")

        if val > max_value:
            max_value = val

    return max_value