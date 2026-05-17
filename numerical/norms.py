def infinity_norm(vector, machine=None):

    if machine is None:
        return max(abs(x) for x in vector)

    values = [
        machine.abs(x)
        for x in vector
    ]

    return max(values)