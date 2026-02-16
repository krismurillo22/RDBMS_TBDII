import tkinter as tk
from tkinter import ttk


class ScrollFrame(ttk.Frame):
    """
    Frame con scroll vertical (Canvas + Scrollbar) para meter contenido grande.
    """
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.vbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)       # Windows
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_mousewheel)

    def _on_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
