import tkinter as tk
from models.point import Point

class CartesianCanvas:
    def __init__(self, root, scale=40):
        self.root = root
        self.scale = scale # Pixels por unidade matemática

        self.points = [] # Lista de objetos Point
        self.segments_reference = [] # Splines calculadas com Float64
        self.segments_finite = []    # Splines calculadas com sua FiniteMachine

        self.drag_point = None
        self.machine = None
        self.view_state = 0 # 0: Ambas, 1: Só Ideal, 2: Só Máquina

        # Configuração do Canvas do Tkinter
        self.canvas = tk.Canvas(
            root,
            bg="#f8f9fa",
            highlightthickness=0,
            cursor="cross"
        )
        
        # Bindings de eventos
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_zoom)

        self.min_scale = 10
        self.max_scale = 400
        self.width = 1
        self.height = 1

    # =====================================================
    # GERENCIAMENTO DE ESTADO
    # =====================================================

    def set_machine(self, machine):
        """Define a máquina finita atual para exibição no HUD."""
        self.machine = machine
        self.redraw()

    def set_segments(self, ref_segments, fin_segments):
        """Recebe os novos segmentos calculados e redesenha a tela."""
        self.segments_reference = ref_segments
        self.segments_finite = fin_segments
        self.redraw()

    def toggle_mode(self, state):
        """Altera o modo de visualização (Destaque)."""
        self.view_state = state
        self.redraw()

    def clear(self):
        """Limpa todos os dados do gráfico."""
        self.points = []
        self.segments_reference = []
        self.segments_finite = []
        self.redraw()

    # =====================================================
    # SISTEMA DE COORDENADAS (Mundo <-> Tela)
    # =====================================================

    def world_to_screen(self, x, y):
        cx, cy = self.width / 2, self.height / 2
        return (cx + float(x) * self.scale, cy - float(y) * self.scale)

    def screen_to_world(self, x, y):
        cx, cy = self.width / 2, self.height / 2
        return ((x - cx) / self.scale, (cy - y) / self.scale)

    # =====================================================
    # EVENTOS DE INTERAÇÃO
    # =====================================================

    def on_resize(self, event):
        self.width = max(1, event.width)
        self.height = max(1, event.height)
        self.redraw()

    def on_zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale = max(self.min_scale, min(self.scale * factor, self.max_scale))
        self.redraw()

    def find_point(self, x, y):
        for p in self.points:
            sx, sy = self.world_to_screen(p.x, p.y)
            if abs(sx - x) < 12 and abs(sy - y) < 12:
                return p
        return None

    def on_click(self, event):
        p = self.find_point(event.x, event.y)
        if p:
            self.drag_point = p
        else:
            wx, wy = self.screen_to_world(event.x, event.y)
            self.points.append(Point(wx, wy))
            self.root.event_generate("<<RebuildRequest>>")
        self.redraw()

    def on_drag(self, event):
        if self.drag_point:
            wx, wy = self.screen_to_world(event.x, event.y)
            self.drag_point.x = wx
            self.drag_point.y = wy
            self.redraw()

    def on_release(self, event):
        if self.drag_point:
            self.root.event_generate("<<RebuildRequest>>")
            self.drag_point = None

    # =====================================================
    # RENDERIZAÇÃO (DESENHO)
    # =====================================================

    def redraw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_axes()
        self.draw_spline() 
        self.draw_points() 
        self.draw_hud()    

    def draw_grid(self):
        step = self.scale
        cx, cy = self.width / 2, self.height / 2
        
        # Linhas Verticais
        x_offset = cx % step
        for x in range(int(x_offset), int(self.width), int(step)):
            self.canvas.create_line(x, 0, x, self.height, fill="#eeeeee")
        
        # Linhas Horizontais
        y_offset = cy % step
        for y in range(int(y_offset), int(self.height), int(step)):
            self.canvas.create_line(0, y, self.width, y, fill="#eeeeee")

    def draw_axes(self):
        cx, cy = self.width / 2, self.height / 2
        self.canvas.create_line(0, cy, self.width, cy, fill="#333333", width=1)
        self.canvas.create_line(cx, 0, cx, self.height, fill="#333333", width=1)

    def draw_points(self):
        for p in self.points:
            x, y = self.world_to_screen(p.x, p.y)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="#ff4444", outline="white", width=2)

    def draw_spline(self):
        # 1. Desenha Referência (Verde) se estiver no modo 0 ou 1
        if self.view_state in [0, 1]:
            self._render_curve(self.segments_reference, color="#2ca02c", width=1, dash=None)
        
        # 2. Desenha Finita (Azul) se estiver no modo 0 ou 2
        if self.view_state in [0, 2]:
            # Se estiver isolada (modo 2), destaca com linha mais grossa
            w = 3 if self.view_state == 2 else 2
            self._render_curve(self.segments_finite, color="#1f77b4", width=w, dash=(5, 2))

    def _render_curve(self, segments, color, width, dash):
        for s in segments:
            x_start, x_end = float(s.x0), float(s.x1)
            if x_end <= x_start: continue

            res = 50 
            step = (x_end - x_start) / res
            coords = []
            
            for i in range(res + 1):
                tx = x_start + i * step
                try:
                    ty = s.evaluate(tx)
                    sx, sy = self.world_to_screen(tx, ty)
                    coords.extend([sx, sy])
                except: continue

            if len(coords) >= 4:
                self.canvas.create_line(coords, fill=color, width=width, dash=dash, smooth=True)

    def draw_hud(self):
        """Legenda dinâmica baseada no estado de visualização."""
        prec = self.machine.precision if self.machine else "?"
        
        # Fundo do HUD
        self.canvas.create_rectangle(10, 10, 240, 70, fill="white", outline="#ccc", width=1)
        
        # Texto da Máquina Atual
        self.canvas.create_text(20, 25, text=f"Máquina: β=10, t={prec}", anchor="w", font=("Arial", 9, "bold"))
        
        # Legendas das linhas
        if self.view_state in [0, 1]:
            self.canvas.create_line(20, 45, 45, 45, fill="#2ca02c", width=2)
            self.canvas.create_text(55, 45, text="Ideal (Float64)", anchor="w", font=("Arial", 9))
            
        if self.view_state in [0, 2]:
            y_pos = 60 if self.view_state == 0 else 45
            self.canvas.create_line(20, y_pos, 45, y_pos, fill="#1f77b4", width=2, dash=(4, 2))
            self.canvas.create_text(55, y_pos, text="Finita (Aritmética Limitada)", anchor="w", font=("Arial", 9))