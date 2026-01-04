import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import BOUNDS

(xmin, xmax), (ymin, ymax), (zmin, zmax) = BOUNDS


class _BaseView(ctk.CTkFrame):
    def __init__(self, master, title, xlim, ylim, figsize):
        super().__init__(master)

        self.title = title
        self.xlim = xlim
        self.ylim = ylim

        # colors
        self.fig_bg = "#1e1e1e"
        self.ax_bg = "#2b2b2b"
        self.fg = "white"

        self.fig = Figure(figsize=figsize, facecolor=self.fig_bg)
        self.ax = self.fig.add_subplot(1, 1, 1)

        self.reset_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=self.fig_bg)
        self.canvas_widget.pack(fill="both", expand=True)

        self.canvas.draw()

    def reset_axes(self):
        """Call after ax.clear() to restore styling/limits."""
        self.ax.set_facecolor(self.ax_bg)
        self.ax.set_title(self.title, pad=4, color=self.fg)

        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)

        self.ax.tick_params(colors=self.fg)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        self.fig.tight_layout(pad=0.2)


class XYView(_BaseView):
    def __init__(self, master):
        super().__init__(
            master=master,
            title="XY Plane",
            xlim=(xmin, xmax),
            ylim=(ymin, ymax),
            figsize=(4, 4),
        )


class XZView(_BaseView):
    def __init__(self, master):
        super().__init__(
            master=master,
            title="XZ Plane",
            xlim=(xmin, xmax),
            ylim=(zmin, zmax),
            figsize=(4, 2),
        )


class YZView(_BaseView):
    def __init__(self, master):
        super().__init__(
            master=master,
            title="YZ Plane",
            xlim=(ymin, ymax),
            ylim=(zmin, zmax),
            figsize=(4, 2),
        )
