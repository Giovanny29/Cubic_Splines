class Point:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __lt__(self, other):
        return self.x < other.x