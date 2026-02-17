import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Any, Dict

from db.execute import run_sql


class SqlRunnerView(ttk.Frame):
    def __init__(self, parent, get_conn: Callable[[], Any], on_back: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.get_conn = get_conn
        self.on_back = on_back

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        ttk.Button(top, text="← Volver", command=self._back).pack(side="left", padx=(0, 8))
        ttk.Label(top, text="Editor SQL", style="Title.TLabel").pack(side="left")

        btns = ttk.Frame(top)
        btns.pack(side="right")
        ttk.Button(btns, text="Ejecutar", command=self.execute).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Limpiar", command=self.clear).pack(side="left")

        editor_box = ttk.Frame(self, padding=(8, 0, 8, 8))
        editor_box.pack(fill="x")

        self.txt_sql = tk.Text(editor_box, height=10, wrap="none")
        self.txt_sql.pack(fill="x")
        self.txt_sql.insert("1.0", "SELECT now() AS server_time;")
        # dark para el Text
        self.txt_sql.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat")

        out_box = ttk.Frame(self, padding=8)
        out_box.pack(fill="both", expand=True)

        ttk.Label(out_box, text="Resultados", style="Section.TLabel").pack(anchor="w")
        self.lbl_msg = ttk.Label(out_box, text="", style="Muted.TLabel")
        self.lbl_msg.pack(anchor="w", pady=(2, 6))

        self.grid = ttk.Treeview(out_box, show="headings")
        self.grid.pack(fill="both", expand=True)

    def _back(self):
        if self.on_back:
            self.on_back()

    def clear(self):
        self.txt_sql.delete("1.0", "end")
        self.lbl_msg.configure(text="")
        self.grid.delete(*self.grid.get_children())
        self.grid["columns"] = ()

    def _load_grid(self, columns, rows):
        self.grid.delete(*self.grid.get_children())
        self.grid["columns"] = columns
        for c in columns:
            self.grid.heading(c, text=c)
            self.grid.column(c, width=160, anchor="w", stretch=True)

        for r in rows[:500]:
            self.grid.insert("", "end", values=r)

        self.lbl_msg.configure(text=f"{len(rows)} fila(s)." if len(rows) <= 500 else f"Mostrando 500 de {len(rows)} filas.")

    def execute(self):
        conn = self.get_conn()
        if conn is None:
            messagebox.showwarning("Sin conexión", "Conéctate primero.")
            return

        sql = self.txt_sql.get("1.0", "end").strip()
        if not sql:
            return

        try:
            result: Dict[str, Any] = run_sql(conn, sql)
            if result["type"] == "query":
                self._load_grid(result.get("columns", []), result.get("rows", []))
            else:
                self.grid.delete(*self.grid.get_children())
                self.grid["columns"] = ()
                self.lbl_msg.configure(text=result.get("message", "OK"))
        except Exception as e:
            self.grid.delete(*self.grid.get_children())
            self.grid["columns"] = ()
            self.lbl_msg.configure(text=f"ERROR: {e}")
