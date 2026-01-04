import customtkinter as ctk

from gui.canvas_views import XYView, XZView, YZView
from gui.log_panel import LogPanel

from simulation.scene import Scene
from simulation.station import Station
from simulation.target import Target
from simulation.tdoa import (
    simulate_arrival_times,
    compute_tdoa,
    range_diff_level,
    range_diff_field,
)
from simulation.localization import estimate_position

import numpy as np
import math


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.scene = Scene()
        self.mode = None  
        self._station_id = 1
        self._target_id = 1
        self._triangle_centroid = None


        self._configure_window()
        self._build_toolbar()
        self._build_main_layout()
        self._build_views()
        self._build_log_panel()

        self._bind_events()
        self._redraw_all()

    # ----------------------------
    # Window
    # ----------------------------
    def _configure_window(self):
        self.title("Multilateration Simulator")
        self.geometry("1200x800")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)   # toolbar
        self.grid_rowconfigure(1, weight=70)  # views
        self.grid_rowconfigure(2, weight=30)  # log

    # ----------------------------
    # Toolbar
    # ----------------------------
    def _build_toolbar(self):
        self.toolbar = ctk.CTkFrame(self, height=50)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        self.toolbar.grid_columnconfigure(10, weight=1)

        self.btn_place_station = ctk.CTkButton(
            self.toolbar, text="Place Station", command=self._set_mode_station
        )
        self.btn_place_station.grid(row=0, column=0, padx=6, pady=8, sticky="w")

        self.btn_triangle = ctk.CTkButton(
            self.toolbar, text="Place Triangle", command=self._set_mode_triangle
        )
        self.btn_triangle.grid(row=0, column=1, padx=6, pady=8, sticky="w")  

        self.btn_place_target = ctk.CTkButton(
            self.toolbar, text="Place Target", command=self._set_mode_target
        )
        self.btn_place_target.grid(row=0, column=2, padx=6, pady=8, sticky="w")

        self.btn_start = ctk.CTkButton(
            self.toolbar, text="Start Simulation", command=self._start_simulation
        )
        self.btn_start.grid(row=0, column=3, padx=6, pady=8, sticky="w")

        self.btn_clear = ctk.CTkButton(
            self.toolbar, text="Clear", command=self._clear_scene
        )
        self.btn_clear.grid(row=0, column=4, padx=6, pady=8, sticky="w")
  


    def _set_mode_triangle(self):
        self.mode = "triangle"
        self.log_panel.write("Mode: TRIANGLE placement. Click centroid in XY.")

    def _set_mode_station(self):
        self.mode = "station"
        self.log_panel.write("Mode: place STATION (click in XY).")

    def _set_mode_target(self):
        self.mode = "target"
        self.log_panel.write("Mode: place TARGET (click in XY).")

    def _clear_scene(self):
        self.scene.reset()
        self._station_id = 1
        self._target_id = 1
        self.log_panel.write("Scene cleared.")
        self._redraw_all()

    # ----------------------------
    # Main layout
    # ----------------------------
    def _build_main_layout(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=65, uniform="views")
        self.main_frame.grid_columnconfigure(1, weight=35, uniform="views")

        self.xy_box = ctk.CTkFrame(self.main_frame)
        self.xy_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.xy_box.grid_rowconfigure(0, weight=1)
        self.xy_box.grid_columnconfigure(0, weight=1)

        self.side_box = ctk.CTkFrame(self.main_frame)
        self.side_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.side_box.grid_columnconfigure(0, weight=1)
        self.side_box.grid_rowconfigure(0, weight=50)
        self.side_box.grid_rowconfigure(1, weight=50)

    def _build_views(self):
        self.xy_view = XYView(self.xy_box)
        self.xy_view.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self.xz_view = XZView(self.side_box)
        self.xz_view.grid(row=0, column=0, sticky="nsew", padx=6, pady=(6, 3))

        self.yz_view = YZView(self.side_box)
        self.yz_view.grid(row=1, column=0, sticky="nsew", padx=6, pady=(3, 6))

    # ----------------------------
    # Log
    # ----------------------------
    def _build_log_panel(self):
        self.log_panel = LogPanel(self)
        self.log_panel.grid(row=2, column=0, sticky="nsew", padx=8, pady=(4, 8))


    # ----------------------------
    # Events
    # ----------------------------
    def _bind_events(self):
        self.xy_view.canvas.mpl_connect("button_press_event", self._on_xy_click)

    def _on_xy_click(self, event):
        xy = self._validate_xy_click(event)
        if xy is None:
            return
        x, y = xy

        handler = {
            "station": self._handle_station_click,
            "target": self._handle_target_click,
            "triangle": self._handle_triangle_click,
        }.get(self.mode)

        if handler is None:
            return

        handler(x, y)
        self._redraw_all()

    def _validate_xy_click(self, event):
        if self.mode not in ("station", "target", "triangle"):
            return None
        if event.inaxes != self.xy_view.ax:
            return None
        if event.xdata is None or event.ydata is None:
            return None
        return float(event.xdata), float(event.ydata)
    
    def _add_station(self, x, y, z, prefix="Added Station"):
        s = Station(self._station_id, (x, y, z))
        try:
            self.scene.add_station(s)
        except ValueError as e:
            self.log_panel.write(f"ERROR: {e}")
            return None

        self.log_panel.write(f"{prefix} {s.id}: ({x:.1f}, {y:.1f}, {z:.1f})")
        self._station_id += 1
        return s
    
    def _handle_station_click(self, x, y):
        z = self._prompt_z(self._station_id)
        if z is None:
            return
        self._add_station(x, y, z)

    def _handle_target_click(self, x, y):
        z = self._prompt_z(self._target_id)
        if z is None:
            return

        t = Target(self._target_id, (x, y, z))
        try:
            self.scene.add_target(t)
        except ValueError as e:
            self.log_panel.write(f"ERROR: {e}")
            return

        self.log_panel.write(f"Added Target {t.id}: ({x:.1f}, {y:.1f}, {z:.1f})")
        self._target_id += 1

    def _handle_triangle_click(self, x, y):
        if self._triangle_centroid is None:
            z = self._prompt_z(self._station_id)
            if z is None:
                return

            self._triangle_centroid = (x, y, z)

            self._add_station(x, y, z, prefix="Triangle centroid station")

            self.log_panel.write(
                f"Triangle centroid set at ({x:.1f}, {y:.1f}, {z:.1f}). Click a vertex to set size."
            )
            return

        centroid = self._triangle_centroid
        vertex_xy = (x, y)

        positions = self._equilateral_triangle_positions_from_centroid_and_vertex(
            centroid, vertex_xy
        )

        for (px, py, pz) in positions:
            self._add_station(px, py, pz, prefix="Triangle vertex station")

        self._triangle_centroid = None  


    def _equilateral_triangle_positions_from_centroid_and_vertex(self, centroid, vertex_xy):
        import math

        cx, cy, _ = centroid
        vx, vy = vertex_xy

        zs = self._prompt_triangle_vertex_zs()
        if zs is None:
            return None
        z1, z2, z3 = zs

        dx = vx - cx
        dy = vy - cy
        R = math.hypot(dx, dy)
        if R == 0:
            raise ValueError("Vertex cannot equal centroid")

        cos120 = -0.5
        sin120 = math.sqrt(3) / 2

        rx1 = dx * cos120 - dy * sin120
        ry1 = dx * sin120 + dy * cos120

        rx2 = dx * cos120 + dy * sin120
        ry2 = -dx * sin120 + dy * cos120

        p1 = (vx, vy, z1)
        p2 = (cx + rx1, cy + ry1, z2)
        p3 = (cx + rx2, cy + ry2, z3)

        return [p1, p2, p3]



    def _prompt_triangle_vertex_zs(self):
        zs = []
        for i in range(1, 4):
            z = self._prompt_z(f" (triangle vertex {i})")
            if z is None:
                return None
            zs.append(z)
        return zs


    def _prompt_z(self, id):
        dialog = ctk.CTkInputDialog(text=f"Enter station{id} Z coordinate:", title="Z value")
        raw = dialog.get_input()
        if raw is None:
            return None
        raw = raw.strip()
        if raw == "":
            return None
        try:
            return float(raw)
        except ValueError:
            self.log_panel.write("ERROR: Z must be a number.")
            return None

    # ----------------------------
    # Drawing
    # ----------------------------
    def _redraw_all(self):
        self._draw_xy()
        self._draw_xz()
        self._draw_yz()

    def _draw_xy(self):
        ax = self.xy_view.ax
        ax.clear()
        self.xy_view.reset_axes()

        for s in self.scene.get_stations():
            x, y, z = s.get_position()
            ax.plot([x], [y], marker="^", markersize=8)
            ax.text(x, y, f"S{s.id}: (z={z})", fontsize=8,color="green")

        for t in self.scene.get_targets():
            x, y, z= t.get_position()
            ax.plot([x], [y], marker="o", markersize=8)
            ax.text(x, y, f"T{t.id}: (z={z})", fontsize=8,color="red")

        self.xy_view.canvas.draw_idle()

    def _draw_xz(self):
        ax = self.xz_view.ax
        ax.clear()
        self.xz_view.reset_axes()

        for s in self.scene.get_stations():
            x, _, z = s.get_position()
            ax.plot([x], [z], marker="^", markersize=6)
            ax.text(x, z, f"S{s.id}", fontsize=8)

        for t in self.scene.get_targets():
            x, _, z = t.get_position()
            ax.plot([x], [z], marker="o", markersize=6)
            ax.text(x, z, f"T{t.id}", fontsize=8)

        self.xz_view.canvas.draw_idle()

    def _draw_yz(self):
        ax = self.yz_view.ax
        ax.clear()
        self.yz_view.reset_axes()

        for s in self.scene.get_stations():
            _, y, z = s.get_position()
            ax.plot([y], [z], marker="^", markersize=6)
            ax.text(y, z, f"S{s.id}", fontsize=8)

        for t in self.scene.get_targets():
            _, y, z = t.get_position()
            ax.plot([y], [z], marker="o", markersize=6)
            ax.text(y, z, f"T{t.id}", fontsize=8)

        self.yz_view.canvas.draw_idle()

    # ----------------------------
    # Simulation
    # ----------------------------
    def _start_simulation(self):
        stations = self.scene.get_stations()
        targets = self.scene.get_targets()

        if len(stations) < 4:
            self.log_panel.write("ERROR: Need at least 4 stations.")
            return
        if len(targets) < 1:
            self.log_panel.write("ERROR: Need at least 1 target.")
            return

        ref_id = stations[0].id  
        self.log_panel.write(f"Starting simulation. Reference station: {ref_id}")

        for t in targets:
            arrival = simulate_arrival_times(t, stations)
            tdoa = compute_tdoa(arrival, reference_id=ref_id)

            est = estimate_position(stations, reference_id=ref_id, tdoa=tdoa, initial_guess=(1000, 1000, 500))

            tx, ty, tz = t.get_position()
            ex, ey, ez = est
            err = ((tx - ex) ** 2 + (ty - ey) ** 2 + (tz - ez) ** 2) ** 0.5

            self.log_panel.write(
                f"T{t.id} true=({tx:.2f},{ty:.2f},{tz:.2f})  "
                f"est=({ex:.2f},{ey:.2f},{ez:.2f})  err={err:.3f} m"
            )

        self._redraw_all()
        self._draw_hyperbolas_for_target(t, stations, ref_id, tdoa)

    #----------------------------
    # Hyperbola Drawing
    #----------------------------
    def _draw_hyperbolas_for_target(self, target, stations, ref_id, tdoa):
        specs = [
            ("xy", self.xy_view, 200, 0, 1, 2),  
            ("xz", self.xz_view, 180, 0, 2, 1),
            ("yz", self.yz_view, 180, 1, 2, 0),
        ]
        for plane, view, n, axis0, axis1, fixed_axis in specs:
            self._draw_hyperbolas_plane(
                plane=plane,
                view=view,
                target=target,
                stations=stations,
                ref_id=ref_id,
                tdoa=tdoa,
                n=n,
                axis0=axis0,
                axis1=axis1,
                fixed_axis=fixed_axis,
            )

    def _draw_hyperbolas_plane(
        self,
        plane: str,
        view,
        target,
        stations,
        ref_id,
        tdoa,
        n: int,
        axis0: int,
        axis1: int,
        fixed_axis: int,
    ):
        bounds = self.scene.bounds  

        fixed_value = target.get_position()[fixed_axis]

        s_ref = next(s for s in stations if s.id == ref_id)
        ref_pos = s_ref.get_position()

        (lo0, hi0) = bounds[axis0]
        (lo1, hi1) = bounds[axis1]

        v0 = np.linspace(lo0, hi0, n)
        v1 = np.linspace(lo1, hi1, n)
        A0, A1 = np.meshgrid(v0, v1)

        ax = view.ax

        for s in stations:
            if s.id == ref_id:
                continue

            F = range_diff_field(A0, A1, plane, fixed_value, s.get_position(), ref_pos)
            level = range_diff_level(tdoa[s.id])
            ax.contour(A0, A1, F, levels=[level], linewidths=1, colors="green")

        view.canvas.draw_idle()
