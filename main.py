"""
Ponto de entrada principal para a aplicação Spline System.
Coordena a Interface do Usuário (UI), a Máquina Finita e os Solucionadores Numéricos.
"""
import tkinter as tk
import ui.canvas
from ui.canvas import CartesianCanvas
from ui.controls import Controls

from spline.spline_builder import build_natural_spline
from numerical.machine import FiniteMachine, RoundingMode

# =====================================================
# CONFIGURAÇÃO DA JANELA PRINCIPAL
# =====================================================
root = tk.Tk()
root.title("Projeto ALA - Spline Cúbica: Máquina Finita vs Referência")
root.geometry("1200x850")
root.configure(bg="#1e1e1e")

# =====================================================
# ESTADO GLOBAL DO SISTEMA
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
# PAINEL DE INFORMAÇÕES E MÉTRICAS
# =====================================================
info_frame = tk.Frame(root, bg="#2d2d2d", height=85, highlightbackground="#444", highlightthickness=1)
info_frame.pack(side=tk.TOP, fill=tk.X)
info_frame.pack_propagate(False)

metrics_label = tk.Label(
    info_frame,
    text="Aguardando pontos... (Mínimo 3 pontos)",
    fg="#00ff00",
    bg="#2d2d2d",
    font=("Consolas", 10),
    justify="left"
)
metrics_label.pack(side=tk.LEFT, padx=20, pady=5)

def update_metrics(result):
    """Atualiza o painel superior com os dados de iteração e erro."""
    if not result:
        metrics_label.config(text="Adicione pelo menos 3 pontos.", fg="#aaa")
        return

    ref = result.get("reference")
    fin = result.get("finite")

    texto = ""
    if ref:
        texto += (
            f"[IDEAL - Float 64-bits]\n"
            f"Iterações: {ref.get('iterations', 1)} | Erro: {ref.get('error', 0.0):.2e}\n"
        )

    if fin:
        cor = "#00ff00" if fin.get('converged') else "#ff5555"
        status_msg = fin.get('status', 'OK')
        
        texto += (
            f"-----------------------------------------------------------\n"
            f"[MÁQUINA FINITA - t={machine.precision} - {fin.get('method', solver_method).upper()}]\n"
            f"Status: {status_msg} | Iterações: {fin.get('iterations', 0)} | Erro: {fin.get('error', 0.0):.6e}"
        )
        metrics_label.config(fg=cor)

    metrics_label.config(text=texto)

# =====================================================
# CANVAS E RECONSTRUÇÃO
# =====================================================
canvas = CartesianCanvas(root)
canvas.set_machine(machine)

def rebuild(event=None):
    """
    Recalcula as splines. Chamado ao interagir com pontos ou mudar configurações.
    """
    if len(canvas.points) < 3:
        canvas.set_segments([], [])
        update_metrics(None)
        return

    try:
        # Chamamos o builder que gerencia os dois solvers
        result = build_natural_spline(
            canvas.points,
            machine,
            method=solver_method
        )

        # Atualiza as curvas no canvas
        canvas.set_segments(
            result["segments_reference"],
            result["segments_finite"]
        )
        
        # Atualiza os textos de erro/iteração
        update_metrics(result)

    except Exception as e:
        print(f"[REBUILD ERROR] {e}")

# Escuta o pedido de reconstrução vindo do Canvas (drag/click)
root.bind("<<RebuildRequest>>", rebuild)

# =====================================================
# AÇÕES E CALLBACKS PARA O CONTROLS
# =====================================================
def clear():
    """Limpa o canvas e reseta as métricas."""
    canvas.clear()
    update_metrics(None)

def toggle_view_mode(state):
    """
    Alterna a visibilidade no Canvas.
    0: Ambas, 1: Só Ideal, 2: Só Máquina
    """
    canvas.toggle_mode(state)

def update_machine(base, precision):
    """Atualiza a precisão da máquina e força novo cálculo."""
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
    """Troca entre Jacobi e Gauss-Seidel."""
    global solver_method
    solver_method = method
    rebuild()

# =====================================================
# INICIALIZAÇÃO DOS CONTROLES
# =====================================================
controls = Controls(
    root,
    on_clear=clear,
    on_build=rebuild,
    on_toggle_mode=toggle_view_mode,
    on_update_machine=update_machine,
    on_switch_solver=switch_solver
)

# Empacota o canvas e inicia o loop
canvas.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    rebuild()
    root.mainloop()