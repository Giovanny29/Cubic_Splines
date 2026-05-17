def is_diagonally_dominant(A):

    n = len(A)

    for i in range(n):

        diagonal = abs(A[i][i])

        row_sum = 0

        for j in range(n):

            if i != j:
                row_sum += abs(A[i][j])

        if diagonal <= row_sum:
            return False

    return True