import tkinter as tk
from models.point import Point


class CartesianCanvas:

    def __init__(self, root, scale=25):

        self.root = root
        self.scale = scale

        self.points = []

        self.segments_reference = []
        self.segments_finite = []

        self.use_machine = True
        self.drag_point = None

        self.machine = None
        self.metrics = None

        self.canvas = tk.Canvas(
            root,
            bg="#f8f9fa",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_zoom)

        self.min_scale = 8
        self.max_scale = 120

        self.width = 1
        self.height = 1

    # =====================================================
    # STATE
    # =====================================================

    def set_machine(self, machine):
        self.machine = machine

    def set_segments(self, result: dict):
        self.segments_reference = result.get("segments_reference", [])
        self.segments_finite = result.get("segments_finite", [])
        self.metrics = result
        self.redraw()

    def clear(self):
        self.points = []
        self.segments_reference = []
        self.segments_finite = []
        self.metrics = None
        self.redraw()

    def toggle_mode(self):
        self.use_machine = not self.use_machine
        self.redraw()

    # =====================================================
    # EVENTS
    # =====================================================

    def on_resize(self, event):
        self.width = max(1, event.width)
        self.height = max(1, event.height)
        self.redraw()

    def on_zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale = max(self.min_scale, min(self.scale * factor, self.max_scale))
        self.redraw()

    # =====================================================
    # COORDS
    # =====================================================

    def world_to_screen(self, x, y):
        cx = self.width / 2
        cy = self.height / 2
        return (cx + x * self.scale, cy - y * self.scale)

    def screen_to_world(self, x, y):
        cx = self.width / 2
        cy = self.height / 2
        return ((x - cx) / self.scale, (cy - y) / self.scale)

    def find_point(self, x, y):
        for p in self.points:
            sx, sy = self.world_to_screen(p.x, p.y)
            if abs(sx - x) < 10 and abs(sy - y) < 10:
                return p
        return None

    def on_click(self, event):
        p = self.find_point(event.x, event.y)

        if p:
            self.drag_point = p
        else:
            x, y = self.screen_to_world(event.x, event.y)
            self.points.append(Point(x, y))

        self.redraw()

    def on_drag(self, event):
        if self.drag_point:
            x, y = self.screen_to_world(event.x, event.y)
            self.drag_point.x = x
            self.drag_point.y = y
            self.redraw()

    def on_release(self, event):
        self.drag_point = None

    # =====================================================
    # RENDER
    # =====================================================

    def redraw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_axes()
        self.draw_ticks()
        self.draw_points()
        self.draw_spline()
        self.draw_hud()

    # =====================================================
    # GRID
    # =====================================================

    def draw_grid(self):

        step = self.scale
        if step <= 0:
            return

        cx = self.width / 2
        cy = self.height / 2

        x = cx % step
        while x < self.width:
            self.canvas.create_line(x, 0, x, self.height, fill="#e6e6e6")
            x += step

        y = cy % step
        while y < self.height:
            self.canvas.create_line(0, y, self.width, y, fill="#e6e6e6")
            y += step

    # =====================================================
    # AXES
    # =====================================================

    def draw_axes(self):
        cx = self.width / 2
        cy = self.height / 2

        self.canvas.create_line(0, cy, self.width, cy, fill="black", width=2)
        self.canvas.create_line(cx, 0, cx, self.height, fill="black", width=2)

    # =====================================================
    # TICKS (CORRIGIDO SIMÉTRICO)
    # =====================================================

    def draw_ticks(self):

        cx = self.width / 2
        cy = self.height / 2

        world_step = 1.0

        if self.scale * world_step < 20:
            world_step = 2.0
        if self.scale * world_step < 20:
            world_step = 5.0

        step = self.scale * world_step

        x = cx
        while x < self.width:
            v = (x - cx) / self.scale
            self.canvas.create_line(x, cy - 5, x, cy + 5, fill="black")
            self.canvas.create_text(x, cy + 15, text=f"{v:.0f}", font=("Arial", 8))
            x += step

        x = cx
        while x > 0:
            v = (x - cx) / self.scale
            self.canvas.create_line(x, cy - 5, x, cy + 5, fill="black")
            self.canvas.create_text(x, cy + 15, text=f"{v:.0f}", font=("Arial", 8))
            x -= step

        y = cy
        while y < self.height:
            v = (cy - y) / self.scale
            self.canvas.create_line(cx - 5, y, cx + 5, y, fill="black")
            self.canvas.create_text(cx + 20, y, text=f"{v:.0f}", font=("Arial", 8))
            y += step

        y = cy
        while y > 0:
            v = (cy - y) / self.scale
            self.canvas.create_line(cx - 5, y, cx + 5, y, fill="black")
            self.canvas.create_text(cx + 20, y, text=f"{v:.0f}", font=("Arial", 8))
            y -= step

    # =====================================================
    # POINTS
    # =====================================================

    def draw_points(self):
        for p in self.points:
            x, y = self.world_to_screen(p.x, p.y)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red", outline="")

    # =====================================================
    # SPLINE
    # =====================================================

    def draw_spline(self):

        segments = (
            self.segments_finite if self.use_machine
            else self.segments_reference
        )

        color = "#1f77b4" if self.use_machine else "#2ca02c"

        for s in segments:

            if s.x1 == s.x0:
                continue

            step = (s.x1 - s.x0) / 80.0
            if step == 0:
                continue

            x = s.x0
            xs, ys = [], []

            while x <= s.x1:
                try:
                    y = s.evaluate(x)
                except:
                    break

                xs.append(x)
                ys.append(y)
                x += step

            for i in range(len(xs) - 1):
                x1, y1 = self.world_to_screen(xs[i], ys[i])
                x2, y2 = self.world_to_screen(xs[i + 1], ys[i + 1])
                self.canvas.create_line(x1, y1, x2, y2, fill=color)

    # =====================================================
    # HUD
    # =====================================================

    def draw_hud(self):

        if not self.metrics:
            return

        method = self.metrics.get("method", "ref")
        it = self.metrics.get("iterations", 0)
        err = float(self.metrics.get("error") or 0.0)

        label = "FINITE" if self.use_machine else "REFERENCE"
        color = "#1f77b4" if self.use_machine else "#2ca02c"

        self.canvas.create_rectangle(
            10, 10, 260, 85,
            fill="#111",
            outline=""
        )

        self.canvas.create_text(
            20, 20,
            anchor="nw",
            fill="white",
            font=("Consolas", 9),
            text=(
                f"{label}\n"
                f"Method: {method}\n"
                f"Iterations: {it}\n"
                f"Error: {err:.6e}"
            )
        )

        self.canvas.create_rectangle(200, 20, 215, 35, fill=color, outline="")
        self.canvas.create_text(220, 27, anchor="w", fill="white", text="curve")