class SplineSegment:

    def __init__(
        self,
        x0,
        x1,
        M0,
        M1,
        y0,
        y1,
        h
    ):

        self.x0 = x0
        self.x1 = x1

        self.M0 = M0
        self.M1 = M1

        self.y0 = y0
        self.y1 = y1

        self.h = h

    def evaluate(self, x):

        term1 = (
            self.M0 * ((self.x1 - x) ** 3)
        ) / (6 * self.h)

        term2 = (
            self.M1 * ((x - self.x0) ** 3)
        ) / (6 * self.h)

        term3 = (
            self.y0 -
            (self.M0 * (self.h ** 2)) / 6
        ) * ((self.x1 - x) / self.h)

        term4 = (
            self.y1 -
            (self.M1 * (self.h ** 2)) / 6
        ) * ((x - self.x0) / self.h)

        return (
            term1 +
            term2 +
            term3 +
            term4
        )

    def contains(self, x):

        return self.x0 <= x <= self.x1