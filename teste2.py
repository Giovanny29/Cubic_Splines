from models.point import Point

from spline.system_generator import (
    generate_natural_spline_system
)

points = [
    Point(0, 0),
    Point(1, 1),
    Point(2, 0),
    Point(3, 1)
]

A, d = generate_natural_spline_system(points)

print("\nSPLINE SYSTEM")
print()

print("A =")

for row in A:
    print(row)

print()

print("d =")
print(d)