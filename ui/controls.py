import tkinter as tk
from tkinter import ttk

class Controls:
    def __init__(
        self,
        root,
        on_clear,
        on_build,
        on_toggle_mode,
        on_update_machine,
        on_switch_solver
    ):
        self.on_update_machine = on_update_machine
        self.on_switch_solver = on_switch_solver
        self.on_toggle_mode = on_toggle_mode # Callback para mudar a visão no Canvas

        # Frame principal
        self.frame = tk.Frame(root, bg="#2d2d2d", pady=5)
        self.frame.pack(side=tk.TOP, fill=tk.X)

        # =====================================================
        # BOTÕES DE AÇÃO (Esquerda)
        # =====================================================
        self.btn_clear = tk.Button(
            self.frame, text="Limpar Tudo", command=on_clear,
            bg="#e74c3c", fg="white", font=("Arial", 9, "bold"),
            relief="flat", padx=10
        )
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        self.btn_build = tk.Button(
            self.frame, text="Recalcular", command=on_build,
            bg="#3498db", fg="white", font=("Arial", 9, "bold"),
            relief="flat", padx=10
        )
        self.btn_build.pack(side=tk.LEFT, padx=5)

        # NOVO: Botão de Destaque (Toggle View)
        self.view_state = 0  # 0: Ambas, 1: Só Ideal, 2: Só Máquina
        self.view_labels = ["Ver: Ambas", "Ver: Só Ideal", "Ver: Só Máquina"]
        
        self.btn_toggle = tk.Button(
            self.frame, text=self.view_labels[0], command=self.handle_toggle_view,
            bg="#9b59b6", fg="white", font=("Arial", 9, "bold"),
            relief="flat", padx=10
        )
        self.btn_toggle.pack(side=tk.LEFT, padx=10)

        # =====================================================
        # SELEÇÃO DO SOLVER (Centro)
        # =====================================================
        self.solver_var = tk.StringVar(value="gauss")
        
        tk.Label(self.frame, text="Método:", bg="#2d2d2d", fg="#aaa").pack(side=tk.LEFT, padx=(15, 5))
        
        for name, mode in [("Gauss-Seidel", "gauss"), ("Jacobi", "jacobi")]:
            tk.Radiobutton(
                self.frame, text=name, variable=self.solver_var,
                value=mode, command=self.apply_solver,
                bg="#2d2d2d", fg="white", selectcolor="#1e1e1e",
                activebackground="#2d2d2d", activeforeground="white"
            ).pack(side=tk.LEFT, padx=2)

        # =====================================================
        # PARÂMETROS DA MÁQUINA (Direita)
        # =====================================================
        
        # Botão Aplicar (Amarelo)
        tk.Button(
            self.frame, text="Aplicar Máquina", command=self.apply_machine,
            bg="#f1c40f", fg="black", font=("Arial", 9, "bold"),
            relief="flat", padx=10
        ).pack(side=tk.RIGHT, padx=10)

        # Entrada de Precisão (t)
        self.precision = tk.Spinbox(self.frame, from_=1, to=16, width=3)
        self.precision.delete(0, "end")
        self.precision.insert(0, "6")
        self.precision.pack(side=tk.RIGHT, padx=5)
        tk.Label(self.frame, text="Precisão (t):", bg="#2d2d2d", fg="white").pack(side=tk.RIGHT)

        # Entrada de Base (β)
        self.base = tk.Entry(self.frame, width=3)
        self.base.insert(0, "10")
        self.base.pack(side=tk.RIGHT, padx=5)
        tk.Label(self.frame, text="Base (β):", bg="#2d2d2d", fg="white").pack(side=tk.RIGHT)

    # =====================================================
    # LÓGICA DE ATUALIZAÇÃO
    # =====================================================

    def handle_toggle_view(self):
        """Alterna entre mostrar as duas curvas, apenas a ideal ou apenas a finita."""
        self.view_state = (self.view_state + 1) % 3
        self.btn_toggle.config(text=self.view_labels[self.view_state])
        self.on_toggle_mode(self.view_state)

    def apply_machine(self):
        """Coleta os dados dos inputs e atualiza a máquina no sistema."""
        try:
            base = int(self.base.get())
            precision = int(self.precision.get())

            if base < 2:
                print("[ERRO] A base deve ser >= 2")
                return
            if precision < 1:
                print("[ERRO] A precisão deve ser >= 1")
                return

            self.on_update_machine(base, precision)

        except ValueError:
            print("[ERRO] Base e Precisão devem ser números inteiros.")
        except Exception as e:
            print(f"[MACHINE ERROR] {e}")

    def apply_solver(self):
        """Notifica a Main sobre a mudança de algoritmo (Jacobi/Gauss)."""
        self.on_switch_solver(self.solver_var.get())