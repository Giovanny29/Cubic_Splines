import ui.canvas
print(ui.canvas.__file__)
import tkinter as tk

from ui.canvas import CartesianCanvas
from ui.controls import Controls

from spline.spline_builder import build_natural_spline
from numerical.machine import FiniteMachine, RoundingMode


# =====================================================
# WINDOW
# =====================================================

root = tk.Tk()
root.title("Spline System - Finite vs Reference Comparison")
root.geometry("1200x800")


# =====================================================
# STATE GLOBAL
# =====================================================

machine = FiniteMachine(
    base=10,
    precision=6,
    exponent_min=-10,
    exponent_max=10,
    rounding=RoundingMode.ROUND
)

solver_method = "gauss"


# =====================================================
# INFO PANEL
# =====================================================

info_frame = tk.Frame(root, bg="#222", height=60)
info_frame.pack(side=tk.TOP, fill=tk.X)
info_frame.pack_propagate(False)

metrics_label = tk.Label(
    info_frame,
    text="",
    fg="white",
    bg="#222",
    font=("Consolas", 10),
    justify="left"
)
metrics_label.pack(side=tk.LEFT, padx=10, pady=5)


def update_metrics(result):

    if not result:
        metrics_label.config(text="Sem dados")
        return

    ref = result.get("reference")
    fin = result.get("finite")

    text = ""

    if ref:
        text += (
            f"[REFERENCE - numpy]\n"
            f"Iterações: {ref.get('iterations', 0)}\n"
            f"Erro: {ref.get('error', 0.0)}\n\n"
        )

    if fin:
        text += (
            f"[FINITE - {fin.get('method', solver_method)}]\n"
            f"Iterações: {fin.get('iterations', 0)}\n"
            f"Erro: {fin.get('error', 0.0):.6e}\n"
            f"Convergiu: {fin.get('converged', False)}"
        )

    metrics_label.config(text=text)


# =====================================================
# CANVAS
# =====================================================

canvas = CartesianCanvas(root)
canvas.set_machine(machine)


# =====================================================
# REBUILD
# =====================================================

def rebuild():

    if len(canvas.points) < 3:
        canvas.set_segments([], [])
        update_metrics(None)
        return

    try:

        result = build_natural_spline(
            canvas.points,
            machine,
            method=solver_method
        )

        canvas.set_segments(
            result["segments_reference"],
            result["segments_finite"]
        )

        update_metrics(result)

    except Exception as e:
        print(f"[REBUILD ERROR] {e}")


# =====================================================
# ACTIONS
# =====================================================

def clear():
    canvas.clear()
    update_metrics(None)


def toggle():
    canvas.toggle_mode()


def update_machine(base, precision):

    global machine

    machine = FiniteMachine(
        base=base,
        precision=precision,
        exponent_min=-10,
        exponent_max=10,
        rounding=RoundingMode.ROUND
    )

    canvas.set_machine(machine)
    rebuild()


def switch_solver(method):

    global solver_method
    solver_method = method
    rebuild()


# =====================================================
# CONTROLS
# =====================================================

controls = Controls(
    root,
    clear,
    rebuild,
    toggle,
    update_machine,
    switch_solver
)


# =====================================================
# CANVAS PACK (IMPORTANTE)
# =====================================================

canvas.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


# =====================================================
# START
# =====================================================

root.mainloop()