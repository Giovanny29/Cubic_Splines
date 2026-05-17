project/
│
├── main.py
│
├── ui/
│ ├── canvas.py
│ └── controls.py
│
├── spline/
│ ├── system_generator.py
│ ├── spline_builder.py
│ ├── spline_segment.py
│ └── spline_evaluator.py
│
├── numerical/
│ ├── machine.py
│ ├── machine_test.py
│ ├── jacobi.py
│ ├── gauss_seidel.py
│ ├── convergence.py
│ └── norms.py
│
├── graphics/
│ └── renderer.py
│
├── models/
│ └── point.py
│
├── utils/
│ ├── constants.py
│ └── helpers.py
│
└── README.md

```text
project/
│
├── main.py
│
├── ui/
│   ├── canvas.py
│   └── controls.py
│
├── spline/
│   ├── system_generator.py
│   ├── spline_builder.py
│   ├── spline_segment.py
│   └── spline_evaluator.py
│
├── numerical/
│   ├── machine.py
│   ├── machine_test.py
│   ├── jacobi.py
│   ├── gauss_seidel.py
│   ├── convergence.py
│   └── norms.py
│
├── graphics/
│   └── renderer.py
│
├── models/
│   └── point.py
│
├── utils/
│   ├── constants.py
│   └── helpers.py
│
└── README.md
```

# Project Description

Natural Cubic Spline interpolation project developed for the Numerical Linear Algebra course.

The project simulates finite precision arithmetic and solves spline interpolation systems using iterative numerical methods.

Implemented methods:

- Jacobi
- Gauss-Seidel

The project also simulates:

- rounding
- truncation
- overflow
- underflow
- propagation of numerical errors

---

# File Structure Explanation

## main.py

Application entry point.

Responsible for:

- creating test cases
- configuring the finite machine
- generating splines
- executing iterative methods
- rendering results

---

# numerical/

Contains all numerical computation modules.

## machine.py

Implements the finite floating-point machine:

F(b,t,k_1,k_2)

Features:

- configurable base
- configurable mantissa precision
- exponent limits
- normalization
- rounding
- truncation
- overflow simulation
- underflow simulation
- finite arithmetic operations

Implements:

- addition
- subtraction
- multiplication
- division

using machine arithmetic.

---

## machine_test.py

Contains validation tests for:

- normalization
- rounding
- truncation
- overflow
- underflow
- cancellation error
- propagation of error

---

## jacobi.py

Implements the Jacobi iterative method:

x*i^{(k+1)}=\frac{1}{a*{ii}}\left(b*i-\sum*{j\neq i}a\_{ij}x_j^{(k)}\right)

All arithmetic operations are executed using the finite machine.

Features:

- convergence detection
- overflow handling
- finite precision simulation

---

## gauss_seidel.py

Implements the Gauss-Seidel iterative method:

x*i^{(k+1)}=\frac{1}{a*{ii}}\left(b*i-\sum*{j<i}a*{ij}x_j^{(k+1)}-\sum*{j>i}a\_{ij}x_j^{(k)}\right)

Uses immediate value updates during iteration.

Usually converges faster than Jacobi.

---

## convergence.py

Contains utilities for convergence analysis.

Currently implements:

- diagonal dominance verification

Used to predict convergence of iterative methods.

---

## norms.py

Implements vector norms.

Currently:

- infinity norm

Used for:

- stopping criteria
- error estimation

---

# spline/

Contains spline interpolation modules.

## system_generator.py

Builds the tridiagonal linear system associated with the natural cubic spline.

Constructs:

AM=d

where:

- (M_i) are spline second derivatives.

Also validates:

- point ordering
- repeated abscissas

---

## spline_builder.py

Responsible for:

- solving the spline system
- reconstructing spline coefficients
- generating spline segments

Uses:

- Jacobi
- Gauss-Seidel

to solve the spline system.

---

## spline_segment.py

Represents a single cubic spline interval.

Implements:

- interval evaluation
- interval containment

Spline equation:

S*i(x)=\frac{M_i(x*{i+1}-x)^3}{6h*i}+\frac{M*{i+1}(x-x*i)^3}{6h_i}+\left(y_i-\frac{M_i h_i^2}{6}\right)\frac{x*{i+1}-x}{h*i}+\left(y*{i+1}-\frac{M\_{i+1}h_i^2}{6}\right)\frac{x-x_i}{h_i}

---

## spline_evaluator.py

Optional utility module.

Can centralize:

- spline evaluation
- sampling
- interpolation queries

Useful for rendering and GUI integration.

---

# graphics/

Rendering modules.

## renderer.py

Responsible for spline visualization.

Features:

- plotting interpolation points
- rendering spline curves
- graphical debugging

Implemented using:

- matplotlib

---

# ui/

Graphical interface modules.

## canvas.py

Interactive Cartesian plane.

Responsible for:

- mouse interaction
- point insertion
- curve updates
- spline visualization

---

## controls.py

GUI controls.

Can include:

- precision configuration
- rounding mode selection
- solver selection
- clear/reset buttons

---

# models/

Data structures.

## point.py

Represents a 2D point:

(x,y)

Used throughout the project.

---

# utils/

Auxiliary utilities.

## constants.py

Stores:

- UI constants
- colors
- rendering parameters
- numerical tolerances

---

## helpers.py

General utility functions.

Can contain:

- formatting
- conversions
- helper validations

---

# Implemented Numerical Topics

- Floating-point arithmetic
- Finite machine simulation
- Mantissa normalization
- Rounding and truncation
- Overflow and underflow
- Cancellation error
- Error propagation
- Jacobi method
- Gauss-Seidel method
- Convergence analysis
- Natural cubic spline interpolation
- Tridiagonal systems

---

# Current Status

[x] Finite machine
[x] Jacobi method
[x] Gauss-Seidel method
[x] Convergence analysis
[x] Natural spline system generation
[x] Spline construction
[x] Spline evaluation
[ ] Interactive GUI
[ ] Real-time rendering
[ ] User controls
