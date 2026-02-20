import re
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Callable, Any, Optional, List


IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class ColSpec:
    name: str = "id"
    dtype: str = "INT8"
    nullable: bool = False
    default: str = ""
    pk: bool = True
    unique: bool = False


class CreateTableView(ttk.Frame):
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
        self.on_back = on_back
        self.on_created = on_created
        self.schema = default_schema
        self.get_databases = get_databases
        self.get_schemas_for_db = get_schemas_for_db
        self.get_current_info = get_current_info
        self.switch_database = switch_database

        self.var_table = tk.StringVar(value="nombre_tabla")

        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        info = self.get_current_info()
        current_db = info.database if info else "defaultdb"

        self.var_db = tk.StringVar(value=current_db)
        self.var_schema = tk.StringVar(value=default_schema)

        ttk.Label(top, text="DB:", style="Sub.TLabel").pack(side="left", padx=(20, 6))
        self.cmb_db = ttk.Combobox(top, textvariable=self.var_db, width=18, state="readonly")
        self.cmb_db.pack(side="left")

        ttk.Label(top, text="Schema:", style="Sub.TLabel").pack(side="left", padx=(12, 6))
        self.cmb_schema = ttk.Combobox(top, textvariable=self.var_schema, width=14, state="readonly")
        self.cmb_schema.pack(side="left")

        ttk.Button(top, text="← Volver", command=self.on_back).pack(side="left", padx=(0, 10))
        ttk.Label(top, text="Crear Tabla", style="Title.TLabel").pack(side="left")

        ttk.Label(top, text="Interfaz visual de creación", style="Sub.TLabel").pack(side="left", padx=(14, 0))

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)

        card1 = ttk.Frame(body, padding=12)
        card1.pack(fill="x", pady=(0, 12))

        ttk.Label(card1, text="Nombre de la Tabla", style="Section.TLabel").pack(anchor="w")
        ent = ttk.Entry(card1, textvariable=self.var_table, width=40)
        ent.pack(fill="x", pady=(8, 0))

        card2 = ttk.Frame(body, padding=12)
        card2.pack(fill="x", pady=(0, 12))

        hdr = ttk.Frame(card2)
        hdr.pack(fill="x")

        ttk.Label(hdr, text="Columnas", style="Section.TLabel").pack(side="left")
        ttk.Button(hdr, text="+ Agregar Columna", command=self.add_column).pack(side="right")

        self.cols_container = ttk.Frame(card2)
        self.cols_container.pack(fill="x", pady=(8, 0))

        hdr_cols = ttk.Frame(self.cols_container)
        hdr_cols.pack(fill="x", pady=(0, 6))

        labels = [
            ("Nombre", 0),
            ("Tipo de Dato", 1),
            ("Nullable", 2),
            ("Valor por Defecto", 3),
            ("PK", 4),
            ("Unique", 5),
            ("Acciones", 6),
        ]

        for text, col in labels:
            lbl = ttk.Label(hdr_cols, text=text, style="Sub.TLabel")
            lbl.grid(row=0, column=col, padx=(0, 8), sticky="w")

        hdr_cols.columnconfigure(0, weight=2)
        hdr_cols.columnconfigure(1, weight=2)
        hdr_cols.columnconfigure(2, weight=1)
        hdr_cols.columnconfigure(3, weight=2)
        hdr_cols.columnconfigure(4, weight=1)
        hdr_cols.columnconfigure(5, weight=1)
        hdr_cols.columnconfigure(6, weight=0)

        def h(lbl, w):
            ttk.Label(hdr, text=lbl, style="Sub.TLabel").pack(side="left", padx=(0, 8))
            hdr.pack_propagate(False)

        self.cols_container = ttk.Frame(card2)
        self.cols_container.pack(fill="x")

        card3 = ttk.Frame(body, padding=12)
        card3.pack(fill="both", expand=True)

        ttk.Label(card3, text="Vista Previa del SQL", style="Section.TLabel").pack(anchor="w")

        self.txt_preview = tk.Text(card3, height=8, wrap="none")
        self.txt_preview.pack(fill="both", expand=True, pady=(8, 0))
        self.txt_preview.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat")
        self.txt_preview.configure(state="disabled")

        bottom = ttk.Frame(self, padding=12)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Cancelar", command=self.on_back).pack(side="right", padx=(8, 0))
        ttk.Button(bottom, text="Crear Tabla", command=self.create_table).pack(side="right")

        self.rows: List[dict] = []
        self.add_column(initial=True)

        self.var_table.trace_add("write", lambda *_: self.refresh_preview())
        self._load_databases()
        self._load_schemas()

        self.cmb_db.bind("<<ComboboxSelected>>", lambda e: self._on_db_changed())
        self.cmb_schema.bind("<<ComboboxSelected>>", lambda e: self._on_schema_changed())

    def add_column(self, initial=False):
        if initial and self.rows:
            return

        spec = ColSpec() if not self.rows else ColSpec(
            name=f"col_{len(self.rows)+1}",
            dtype="STRING",
            nullable=True,
            default="",
            pk=False,
            unique=False,
        )

        row = self._create_row(self.cols_container, len(self.rows), spec)
        self.rows.append(row)
        self.refresh_preview()

    def _create_row(self, parent, idx: int, spec: ColSpec):
        v_name = tk.StringVar(value=spec.name)
        v_type = tk.StringVar(value=spec.dtype)
        v_nullable = tk.BooleanVar(value=spec.nullable)
        v_default = tk.StringVar(value=spec.default)
        v_pk = tk.BooleanVar(value=spec.pk)
        v_unique = tk.BooleanVar(value=spec.unique)

        frm = ttk.Frame(parent)
        frm.pack(fill="x", pady=4)

        frm.columnconfigure(0, weight=2)
        frm.columnconfigure(1, weight=2)
        frm.columnconfigure(2, weight=1)
        frm.columnconfigure(3, weight=2)
        frm.columnconfigure(4, weight=1)
        frm.columnconfigure(5, weight=1)
        frm.columnconfigure(6, weight=0)

        e_name = ttk.Entry(frm, textvariable=v_name)
        e_name.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        types = ["INT8", "INT4", "STRING", "DECIMAL(12,2)", "BOOL", "TIMESTAMPTZ", "DATE", "UUID"]
        cmb = ttk.Combobox(frm, textvariable=v_type, values=types, state="readonly", width=14)
        cmb.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        chk_null = ttk.Checkbutton(frm, variable=v_nullable)
        chk_null.grid(row=0, column=2, sticky="w", padx=(0, 8))

        e_def = ttk.Entry(frm, textvariable=v_default)
        e_def.grid(row=0, column=3, sticky="ew", padx=(0, 8))

        chk_pk = ttk.Checkbutton(frm, variable=v_pk)
        chk_pk.grid(row=0, column=4, sticky="w", padx=(0, 8))

        chk_uq = ttk.Checkbutton(frm, variable=v_unique)
        chk_uq.grid(row=0, column=5, sticky="w", padx=(0, 8))

        btn_del = ttk.Button(frm, text="🗑", width=3, command=lambda: self.remove_row(frm))
        btn_del.grid(row=0, column=6, sticky="e")

        def on_pk_change(*_):
            if v_pk.get():
                v_nullable.set(False)
            self.refresh_preview()

        def on_any_change(*_):
            self.refresh_preview()

        v_pk.trace_add("write", on_pk_change)
        v_name.trace_add("write", on_any_change)
        v_type.trace_add("write", on_any_change)
        v_nullable.trace_add("write", on_any_change)
        v_default.trace_add("write", on_any_change)
        v_unique.trace_add("write", on_any_change)

        return {
            "frame": frm,
            "name": v_name,
            "type": v_type,
            "nullable": v_nullable,
            "default": v_default,
            "pk": v_pk,
            "unique": v_unique,
        }

    def remove_row(self, frame):
        if len(self.rows) <= 1:
            messagebox.showwarning("Aviso", "La tabla debe tener al menos 1 columna.")
            return

        for i, r in enumerate(self.rows):
            if r["frame"] == frame:
                self.rows.pop(i)
                break

        frame.destroy()
        self.refresh_preview()

    def _quote(self, ident: str) -> str:
        return f'"{ident}"'

    def build_sql(self) -> str:
        table = self.var_table.get().strip()
        if not table:
            return "-- Ingresa el nombre de la tabla para ver la vista previa"
        if not IDENT_RE.match(table):
            return "-- Nombre de tabla inválido. Usa letras, números y _ (no iniciar con número)."

        cols = []
        pk_cols = []

        for r in self.rows:
            name = r["name"].get().strip()
            dtype = r["type"].get().strip()
            nullable = r["nullable"].get()
            default = r["default"].get().strip()
            pk = r["pk"].get()
            unique = r["unique"].get()

            if not name or not IDENT_RE.match(name):
                return "-- Hay un nombre de columna inválido."

            line = f"  {self._quote(name)} {dtype}"

            if not nullable:
                line += " NOT NULL"

            if default and default.upper() != "NULL":
                line += f" DEFAULT {default}"

            if unique and not pk:
                line += " UNIQUE"

            cols.append(line)

            if pk:
                pk_cols.append(name)

        constraints = []
        if pk_cols:
            pk_list = ", ".join(self._quote(c) for c in pk_cols)
            constraints.append(f"  CONSTRAINT {self._quote(table + '_pkey')} PRIMARY KEY ({pk_list})")

        all_lines = cols + constraints
        cols_sql = ",\n".join(all_lines)

        schema = self.var_schema.get().strip() or "public"
        return f'CREATE TABLE {self._quote(schema)}.{self._quote(table)} (\n{cols_sql}\n);'
    
    def refresh_preview(self):
        sql = self.build_sql()
        self.txt_preview.configure(state="normal")
        self.txt_preview.delete("1.0", "end")
        self.txt_preview.insert("1.0", sql)
        self.txt_preview.configure(state="disabled")

    def create_table(self):
        sql = self.build_sql()
        if sql.startswith("--"):
            messagebox.showerror("Error", sql.replace("-- ", ""))
            return

        target_db = self.var_db.get().strip()
        try:
            self.switch_database(target_db)  
        except Exception as e:
            messagebox.showerror("Error", "No se pudo cambiar a la base")
            return

        conn = self.get_conn()              
        if conn is None:
            messagebox.showwarning("Sin conexión", "Conéctate primero.")
            return

        try:
            from db.execute import run_sql
            res = run_sql(conn, sql)
            messagebox.showinfo("OK", res.get("message", "Tabla creada."))
            if self.on_created:
                self.on_created()
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", str(e))

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

    def _on_schema_changed(self):
        self.refresh_preview()
