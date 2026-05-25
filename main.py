"""
Ponto de entrada principal para a aplicação Spline System.
Coordena a Interface do Usuário (UI), a Máquina Finita e os Solucionadores Numéricos.
"""
import tkinter as tk
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
# PAINEL DE INFORMAÇÕES E MÉTRICAS (HUD Superior)
# =====================================================
info_frame = tk.Frame(root, bg="#2d2d2d", height=95, highlightbackground="#444", highlightthickness=1)
info_frame.pack(side=tk.TOP, fill=tk.X)
info_frame.pack_propagate(False)

metrics_label = tk.Label(
    info_frame,
    text="Aguardando pontos... (Mínimo 3 pontos clicados no gráfico)",
    fg="#00ff00",
    bg="#2d2d2d",
    font=("Consolas", 10),
    justify="left"
)
metrics_label.pack(side=tk.LEFT, padx=20, pady=5)

def update_metrics(result):
    """Atualiza o painel superior com os dados de iteração e erro."""
    if not result:
        metrics_label.config(text="Adicione pelo menos 3 pontos no canvas para iniciar os solvers.", fg="#aaa")
        return

    ref = result.get("reference")
    fin = result.get("finite")

    texto = ""
    if ref:
        texto += (
            f"[IDEAL - Float 64-bits Nativo]\n"
            f"Iterações: {ref.get('iterations', 1)} | Erro do Solver: {ref.get('error', 0.0):.2e}\n"
        )

    if fin:
        cor = "#00ff00" if fin.get('converged') else "#ff5555"
        status_msg = fin.get('status', 'OK')
        
        # 💎 UX Melhorada: Formatação dinâmica do erro usando a precisão de máquina (t) definida pelo usuário
        texto += (
            f"---------------------------------------------------------------------------------\n"
            f"[MÁQUINA FINITA - β={machine.base}, t={machine.precision} - Método: {fin.get('method', solver_method).upper()}]\n"
            f"Status: {status_msg} | Iterações: {fin.get('iterations', 0)} | Erro de Convergência: {fin.get('error', 0.0):.{machine.precision}e}"
        )
        metrics_label.config(fg=cor)

    metrics_label.config(text=texto)

# =====================================================
# INTERFACE E COMPONENTES GRÁFICOS
# =====================================================

# 1. Instancia a barra de ferramentas superior (abaixo do HUD de métricas)
controls = Controls(
    root,
    on_clear=lambda: clear(),
    on_build=lambda: rebuild(),
    on_toggle_mode=lambda state: toggle_view_mode(state),
    on_update_machine=lambda b, p: update_machine(b, p),
    on_switch_solver=lambda m: switch_solver(m)
)

# 2. Instancia o Canvas e garante o empacotamento correto ocupando o resto do espaço inferior
canvas = CartesianCanvas(root)
canvas.set_machine(machine)
canvas.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# =====================================================
# AÇÕES E CALLBACKS DE CONTROLE CONTRA FLUXO
# =====================================================
def rebuild(event=None):
    """
    Recalcula as splines. Chamado ao interagir com pontos ou mudar configurações.
    """
    if len(canvas.points) < 3:
        canvas.set_segments([], [])
        update_metrics(None)
        return

    try:
        # Executa o motor numérico global passando a configuração da máquina atual
        result = build_natural_spline(
            canvas.points,
            machine,
            method=solver_method
        )

        # Atualiza as curvas no canvas para renderização matemática poligonal
        canvas.set_segments(
            result["segments_reference"],
            result["segments_finite"]
        )
        
        # Atualiza o HUD dinâmico
        update_metrics(result)

    except Exception as e:
        print(f"[REBUILD ERROR] Falha na orquestração dos nós: {e}")

# Vincula o evento customizado disparado pelos cliques do mouse do canvas
root.bind("<<RebuildRequest>>", rebuild)

def clear():
    """Limpa o canvas e reseta as métricas."""
    canvas.clear()
    update_metrics(None)

def toggle_view_mode(state):
    """Alterna a visibilidade das curvas (Ambas / Só Ideal / Só Máquina)."""
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
    """Troca o algoritmo de relaxamento entre Jacobi e Gauss-Seidel."""
    global solver_method
    solver_method = method
    rebuild()

# =====================================================
# INICIALIZAÇÃO DO LOOP DA APLICAÇÃO
# =====================================================
if __name__ == "__main__":
    # Garante um ciclo inicial de limpeza de tela antes de abrir o loop principal
    rebuild()
    root.mainloop()