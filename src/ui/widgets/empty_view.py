from tkinter import ttk

class EmptyView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Selecciona una tabla para ver detalles", style="Muted.TLabel").pack(
            anchor="center", expand=True
        )
