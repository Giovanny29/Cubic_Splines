class SplineSegment:

    def __init__(self, x0, x1, M0, M1, y0, y1):

        self.x0 = float(x0)
        self.x1 = float(x1)

        self.M0 = float(M0)
        self.M1 = float(M1)

        self.y0 = float(y0)
        self.y1 = float(y1)

        self.h = self.x1 - self.x0

        if self.h == 0:
            raise ValueError("Invalid spline segment: x0 == x1")

    def evaluate(self, x):

        x = float(x)
        h = self.h

        if h == 0:
            raise ValueError("Invalid segment length (h=0)")

        term1 = (self.M0 * ((self.x1 - x) ** 3)) / (6 * h)
        term2 = (self.M1 * ((x - self.x0) ** 3)) / (6 * h)

        term3 = (
            (self.y0 - (self.M0 * (h ** 2)) / 6)
            * ((self.x1 - x) / h)
        )

        term4 = (
            (self.y1 - (self.M1 * (h ** 2)) / 6)
            * ((x - self.x0) / h)
        )

        return term1 + term2 + term3 + term4

    def contains(self, x):
        return self.x0 <= x <= self.x1

    def __repr__(self):
        return f"SplineSegment(x0={self.x0}, x1={self.x1})"