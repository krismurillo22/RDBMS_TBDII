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
        get_databases: Callable[[], list[str]],
        get_schemas_for_db: Callable[[str], list[str]],
        get_current_info: Callable[[], Any],
        switch_database: Callable[[str], None],
        on_back: Callable[[], None],
        on_created: Optional[Callable[[], None]] = None,
        default_schema: str = "public",
    ):
        super().__init__(parent)
        self.get_conn = get_conn
        self.get_databases = get_databases
        self.get_schemas_for_db = get_schemas_for_db
        self.get_current_info = get_current_info
        self.switch_database = switch_database
        self.on_back = on_back
        self.on_created = on_created

        self.var_view = tk.StringVar(value="nombre_vista")

        info = self.get_current_info()
        current_db = info.database if info else "defaultdb"

        self.var_db = tk.StringVar(value=current_db)
        self.var_schema = tk.StringVar(value=default_schema)

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="← Volver", command=self.on_back).pack(side="left", padx=(0, 10))
        ttk.Label(top, text="Crear Vista", style="Title.TLabel").pack(side="left")
        ttk.Label(top, text="Interfaz visual de creación", style="Sub.TLabel").pack(side="left", padx=(14, 0))

        ttk.Label(top, text="DB:", style="Sub.TLabel").pack(side="right", padx=(8, 6))
        self.cmb_db = ttk.Combobox(top, textvariable=self.var_db, width=18, state="readonly")
        self.cmb_db.pack(side="right")

        ttk.Label(top, text="Schema:", style="Sub.TLabel").pack(side="right", padx=(12, 6))
        self.cmb_schema = ttk.Combobox(top, textvariable=self.var_schema, width=14, state="readonly")
        self.cmb_schema.pack(side="right")

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        card1 = ttk.Frame(body, padding=12)
        card1.pack(fill="x", pady=(0, 12))

        ttk.Label(card1, text="Nombre de la Vista", style="Section.TLabel").pack(anchor="w")
        ttk.Entry(card1, textvariable=self.var_view).pack(fill="x", pady=(8, 0))

        card2 = ttk.Frame(body, padding=12)
        card2.pack(fill="both", expand=True, pady=(0, 12))

        ttk.Label(card2, text="Consulta SQL", style="Section.TLabel").pack(anchor="w")
        self.txt_query = tk.Text(card2, height=10, wrap="none")
        self.txt_query.pack(fill="both", expand=True, pady=(8, 0))
        self.txt_query.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat")
        self.txt_query.insert("1.0", 'SELECT * FROM "public"."clientes";')

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
        self.cmb_db.bind("<<ComboboxSelected>>", lambda e: self._on_db_changed())
        self.cmb_schema.bind("<<ComboboxSelected>>", lambda e: self.refresh_preview())
        self._load_databases()
        self._load_schemas()
        self.refresh_preview()

    def _quote(self, ident: str) -> str:
        return f'"{ident}"'

    def _load_databases(self):
        try:
            dbs = self.get_databases() or []
            self.cmb_db["values"] = dbs
            if dbs and self.var_db.get() not in dbs:
                self.var_db.set(dbs[0])
        except Exception:
            self.cmb_db["values"] = []

    def _load_schemas(self):
        try:
            db = self.var_db.get().strip()
            schemas = self.get_schemas_for_db(db) or []
            self.cmb_schema["values"] = schemas
            if schemas and self.var_schema.get() not in schemas:
                self.var_schema.set("public" if "public" in schemas else schemas[0])
        except Exception:
            self.cmb_schema["values"] = ["public"]
            if not self.var_schema.get():
                self.var_schema.set("public")

    def _on_db_changed(self):
        self._load_schemas()
        self.refresh_preview()

    def build_sql(self) -> str:
        name = self.var_view.get().strip()
        q = self.txt_query.get("1.0", "end").strip()

        if not name:
            return "-- Ingresa el nombre de la vista"
        if not IDENT_RE.match(name):
            return "-- Nombre de vista inválido."
        if not q.lower().startswith("select"):
            return "-- La vista debe empezar con SELECT"

        schema = self.var_schema.get().strip() or "public"
        return f'CREATE VIEW {self._quote(schema)}.{self._quote(name)} AS\n{q};'

    def refresh_preview(self):
        sql = self.build_sql()
        self.txt_preview.configure(state="normal")
        self.txt_preview.delete("1.0", "end")
        self.txt_preview.insert("1.0", sql)
        self.txt_preview.configure(state="disabled")

    def create_view(self):
        sql = self.build_sql()
        if sql.startswith("--"):
            messagebox.showerror("Error", sql.replace("-- ", ""))
            return

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

        try:
            from db.execute import run_sql
            res = run_sql(conn, sql)
            messagebox.showinfo("OK", res.get("message", "Vista creada."))
            if self.on_created:
                self.on_created()
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", str(e))