import re
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Any, Optional

IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class CreateViewView(ttk.Frame):
    def __init__(
        self,
        parent,
        get_conn: Callable[[], Any],
        on_back: Callable[[], None],
        on_created: Optional[Callable[[], None]] = None,
        default_schema: str = "public",
    ):
        super().__init__(parent)
        self.get_conn = get_conn
        self.on_back = on_back
        self.on_created = on_created
        self.schema = default_schema

        self.var_view = tk.StringVar(value="nombre_vista")

        # Header
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="← Volver", command=self.on_back).pack(side="left", padx=(0, 10))
        ttk.Label(top, text="Crear Vista", style="Title.TLabel").pack(side="left")

        ttk.Label(top, text="Interfaz visual de creación", style="Sub.TLabel").pack(side="left", padx=(14, 0))

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        # Card: name
        card1 = ttk.Frame(body, padding=12)
        card1.pack(fill="x", pady=(0, 12))

        ttk.Label(card1, text="Nombre de la Vista", style="Section.TLabel").pack(anchor="w")
        ttk.Entry(card1, textvariable=self.var_view).pack(fill="x", pady=(8, 0))

        # Card: query
        card2 = ttk.Frame(body, padding=12)
        card2.pack(fill="both", expand=True, pady=(0, 12))

        ttk.Label(card2, text="Consulta SQL (SELECT ...)", style="Section.TLabel").pack(anchor="w")
        self.txt_query = tk.Text(card2, height=10, wrap="none")
        self.txt_query.pack(fill="both", expand=True, pady=(8, 0))
        self.txt_query.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat")
        self.txt_query.insert("1.0", "SELECT * FROM public.clientes;")

        # Preview
        card3 = ttk.Frame(body, padding=12)
        card3.pack(fill="x")

        ttk.Label(card3, text="Vista Previa del SQL", style="Section.TLabel").pack(anchor="w")
        self.txt_preview = tk.Text(card3, height=6, wrap="none")
        self.txt_preview.pack(fill="x", pady=(8, 0))
        self.txt_preview.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat")
        self.txt_preview.configure(state="disabled")

        bottom = ttk.Frame(self, padding=12)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Cancelar", command=self.on_back).pack(side="right", padx=(8, 0))
        ttk.Button(bottom, text="Crear Vista", command=self.create_view).pack(side="right")

        self.var_view.trace_add("write", lambda *_: self.refresh_preview())
        self.txt_query.bind("<KeyRelease>", lambda e: self.refresh_preview())
        self.refresh_preview()

    def _quote(self, ident: str) -> str:
        return f'"{ident}"'

    def build_sql(self) -> str:
        name = self.var_view.get().strip()
        q = self.txt_query.get("1.0", "end").strip()

        if not name:
            return "-- Ingresa el nombre de la vista"
        if not IDENT_RE.match(name):
            return "-- Nombre de vista inválido."
        if not q.lower().startswith("select"):
            return "-- La vista debe empezar con SELECT"

        return f'CREATE VIEW {self._quote(self.schema)}.{self._quote(name)} AS\n{q};'

    def refresh_preview(self):
        sql = self.build_sql()
        self.txt_preview.configure(state="normal")
        self.txt_preview.delete("1.0", "end")
        self.txt_preview.insert("1.0", sql)
        self.txt_preview.configure(state="disabled")

    def create_view(self):
        conn = self.get_conn()
        if conn is None:
            messagebox.showwarning("Sin conexión", "Conéctate primero.")
            return

        sql = self.build_sql()
        if sql.startswith("--"):
            messagebox.showerror("Error", sql.replace("-- ", ""))
            return

        try:
            from db.execute import run_sql
            res = run_sql(conn, sql)
            messagebox.showinfo("OK", res.get("message", "Vista creada."))
            if self.on_created:
                self.on_created()
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", str(e))
