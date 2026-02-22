import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Any, Dict, List

from db.execute import run_sql

class SqlRunnerView(ttk.Frame):
    def __init__(
        self,
        parent,
        get_conn: Callable[[], Any],
        get_databases: Callable[[], List[str]],
        get_current_info: Callable[[], Any],
        switch_database: Callable[[str], None],
        on_back: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.get_conn = get_conn
        self.get_databases = get_databases
        self.get_current_info = get_current_info
        self.switch_database = switch_database
        self.on_back = on_back

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        ttk.Button(top, text="← Volver", command=self._back).pack(side="left", padx=(0, 8))
        ttk.Label(top, text="Editor SQL", style="Title.TLabel").pack(side="left")

        info = self.get_current_info()
        current_db = info.database if info else "defaultdb"
        self.var_db = tk.StringVar(value=current_db)

        ttk.Label(top, text="DB:", style="Sub.TLabel").pack(side="right", padx=(8, 6))
        self.cmb_db = ttk.Combobox(top, textvariable=self.var_db, width=18, state="readonly")
        self.cmb_db.pack(side="right")
        self.cmb_db.bind("<<ComboboxSelected>>", lambda e: self._on_db_changed())

        btns = ttk.Frame(top)
        btns.pack(side="right", padx=(12, 0))
        ttk.Button(btns, text="Ejecutar", command=self.execute).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Limpiar", command=self.clear).pack(side="left")

        editor_box = ttk.Frame(self, padding=(8, 0, 8, 8))
        editor_box.pack(fill="x")

        self.txt_sql = tk.Text(editor_box, height=10, wrap="none")
        self.txt_sql.pack(fill="x")
        self.txt_sql.insert("1.0", "SELECT now() AS server_time;")
        self.txt_sql.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat")

        out_box = ttk.Frame(self, padding=8)
        out_box.pack(fill="both", expand=True)

        ttk.Label(out_box, text="Resultados", style="Section.TLabel").pack(anchor="w")
        self.lbl_msg = ttk.Label(out_box, text="", style="Muted.TLabel")
        self.lbl_msg.pack(anchor="w", pady=(2, 6))

        self.grid = ttk.Treeview(out_box, show="headings")
        self.grid.pack(fill="both", expand=True)
        self._load_databases()

    def _back(self):
        if self.on_back:
            self.on_back()

    def _load_databases(self):
        try:
            dbs = self.get_databases() or []
            self.cmb_db["values"] = dbs
            if dbs and self.var_db.get() not in dbs:
                self.var_db.set(dbs[0])
        except Exception:
            self.cmb_db["values"] = []

    def _on_db_changed(self):
        target_db = self.var_db.get().strip()
        try:
            self.switch_database(target_db)
            info = self.get_current_info()
            if info:
                self.lbl_msg.configure(text=f"Conectado a DB: {info.database}")
            else:
                self.lbl_msg.configure(text=f"DB seleccionada: {target_db}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar a la base '{target_db}':\n{e}")

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

        self.lbl_msg.configure(
            text=f"{len(rows)} fila(s)." if len(rows) <= 500 else f"Mostrando 500 de {len(rows)} filas."
        )

    def execute(self):
        target_db = self.var_db.get().strip()
        try:
            self.switch_database(target_db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar a la base '{target_db}':\n{e}")
            return

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