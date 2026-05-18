import tkinter as tk


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

        self.on_switch_solver = on_switch_solver

        self.frame = tk.Frame(root, bg="#1e1e1e")
        self.frame.pack(side=tk.TOP, fill=tk.X)

        # =====================================================
        # BUTTONS
        # =====================================================

        tk.Button(
            self.frame,
            text="Clear",
            command=on_clear,
            bg="#e74c3c",
            fg="white"
        ).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(
            self.frame,
            text="Generate",
            command=on_build,
            bg="#3498db",
            fg="white"
        ).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(
            self.frame,
            text="Toggle View",
            command=on_toggle_mode,
            bg="#2ecc71",
            fg="white"
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # =====================================================
        # SOLVER SWITCH
        # =====================================================

        self.solver_var = tk.StringVar(value="gauss")

        tk.Radiobutton(
            self.frame,
            text="Gauss-Seidel",
            variable=self.solver_var,
            value="gauss",
            command=self.apply_solver,
            bg="#1e1e1e",
            fg="white",
            activebackground="#2c2c2c",
            selectcolor="#2c2c2c"
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            self.frame,
            text="Jacobi",
            variable=self.solver_var,
            value="jacobi",
            command=self.apply_solver,
            bg="#1e1e1e",
            fg="white",
            activebackground="#2c2c2c",
            selectcolor="#2c2c2c"
        ).pack(side=tk.LEFT, padx=5)

        # =====================================================
        # MACHINE PARAMS
        # =====================================================

        tk.Label(self.frame, text="Base", bg="#1e1e1e", fg="white").pack(side=tk.RIGHT)

        self.base = tk.Entry(self.frame, width=5)
        self.base.insert(0, "10")
        self.base.pack(side=tk.RIGHT, padx=5)

        tk.Label(self.frame, text="Precision", bg="#1e1e1e", fg="white").pack(side=tk.RIGHT)

        self.precision = tk.Entry(self.frame, width=5)
        self.precision.insert(0, "6")
        self.precision.pack(side=tk.RIGHT, padx=5)

        tk.Button(
            self.frame,
            text="Apply Machine",
            command=self.apply_machine,
            bg="#f1c40f"
        ).pack(side=tk.RIGHT, padx=5)

        self.on_update_machine = on_update_machine

        # =====================================================
        # IMPORTANTE: NÃO DISPARAR CALLBACK NO INIT
        # =====================================================
        # Antes isso causava rebuild prematuro e crash.
        # Agora o estado inicial fica neutro.
        # =====================================================

    # =====================================================
    # MACHINE
    # =====================================================

    def apply_machine(self):

        try:
            base = int(self.base.get())
            precision = int(self.precision.get())

            if base < 2:
                raise ValueError("Base must be >= 2")

            if precision < 1:
                raise ValueError("Precision must be >= 1")

            self.on_update_machine(base, precision)

        except Exception as e:
            print(f"[MACHINE ERROR] {e}")

    # =====================================================
    # SOLVER SWITCH
    # =====================================================

    def apply_solver(self):
        self.on_switch_solver(self.solver_var.get())