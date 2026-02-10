import tkinter as tk
from db.init_db import init_db
from db.connection import get_connection
from tkinter import ttk, messagebox

# MODALES
class ConnectionDialog(tk.Toplevel):
    def __init__(self, master, title="Modificar Conexión", initial=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=master.COL_BG)
        self.transient(master)
        self.grab_set()

        self.result = None
        initial = initial or {}

        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self, style="Panel.TFrame")
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        self.var_name = tk.StringVar(value=initial.get("name", "postgres"))
        self.var_host = tk.StringVar(value=initial.get("host", "localhost"))
        self.var_port = tk.StringVar(value=str(initial.get("port", 5432)))
        self.var_db = tk.StringVar(value=initial.get("database", "postgres"))
        self.var_user = tk.StringVar(value=initial.get("user", "postgres"))
        self.var_ssl = tk.StringVar(value=initial.get("sslmode", "disable"))

        ttk.Label(frm, text="Nombre:", style="Small.TLabel").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_name, width=32).grid(row=0, column=1, **pad)

        ttk.Label(frm, text="Host:", style="Small.TLabel").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_host, width=32).grid(row=1, column=1, **pad)

        ttk.Label(frm, text="Puerto:", style="Small.TLabel").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_port, width=32).grid(row=2, column=1, **pad)

        ttk.Label(frm, text="Database:", style="Small.TLabel").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_db, width=32).grid(row=3, column=1, **pad)

        ttk.Label(frm, text="Usuario:", style="Small.TLabel").grid(row=4, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_user, width=32).grid(row=4, column=1, **pad)

        ttk.Label(frm, text="SSL Mode:", style="Small.TLabel").grid(row=5, column=0, sticky="w", **pad)
        ttk.Combobox(frm, textvariable=self.var_ssl,
                     values=["disable", "require", "verify-ca", "verify-full"],
                     state="readonly", width=29).grid(row=5, column=1, **pad)

        btns = ttk.Frame(frm, style="Panel.TFrame")
        btns.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 6))
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)

        ttk.Button(btns, text="Cancelar", command=self._cancel).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btns, text="Guardar", style="Primary.TButton", command=self._ok)\
            .grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.bind("<Escape>", lambda *_: self._cancel())
        self.bind("<Return>", lambda *_: self._ok())
        self._center(master)

    def _ok(self):
        self.result = {
            "name": self.var_name.get().strip() or "conexion",
            "host": self.var_host.get().strip() or "localhost",
            "port": int(self.var_port.get().strip() or "5432"),
            "database": self.var_db.get().strip() or "db",
            "user": self.var_user.get().strip() or "user",
            "sslmode": self.var_ssl.get().strip() or "disable",
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    def _center(self, master):
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class UserDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Crear Usuario")
        self.resizable(False, False)
        self.configure(bg=master.COL_BG)
        self.transient(master)
        self.grab_set()

        self.result_sql = None

        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self, style="Panel.TFrame")
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        self.var_username = tk.StringVar()
        self.var_password = tk.StringVar()
        self.var_role = tk.StringVar(value="readwrite")

        ttk.Label(frm, text="Username:", style="Small.TLabel").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_username, width=32).grid(row=0, column=1, **pad)

        ttk.Label(frm, text="Password:", style="Small.TLabel").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_password, width=32, show="•").grid(row=1, column=1, **pad)

        ttk.Label(frm, text="Rol:", style="Small.TLabel").grid(row=2, column=0, sticky="w", **pad)
        ttk.Combobox(frm, textvariable=self.var_role,
                     values=["readonly", "readwrite", "admin"],
                     state="readonly", width=29).grid(row=2, column=1, **pad)

        ttk.Label(frm, text="SQL Generado (preview):", style="Small.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 4)
        )

        self.preview = tk.Text(frm, height=7, width=58,
                               bg=master.COL_PANEL2, fg=master.COL_TEXT,
                               insertbackground=master.COL_TEXT,
                               relief="flat", font=("Consolas", 10))
        self.preview.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        for v in (self.var_username, self.var_password, self.var_role):
            v.trace_add("write", lambda *_: self._refresh_preview())
        self._refresh_preview()

        btns = ttk.Frame(frm, style="Panel.TFrame")
        btns.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 6))
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)

        ttk.Button(btns, text="Cerrar", command=self._cancel).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btns, text="Generar", style="Primary.TButton", command=self._ok)\
            .grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.bind("<Escape>", lambda *_: self._cancel())
        self.bind("<Return>", lambda *_: self._ok())
        self._center(master)

    def _refresh_preview(self):
        u = self.var_username.get().strip() or "nuevo_usuario"
        p = self.var_password.get().strip() or "********"
        role = self.var_role.get().strip()

        grants = {
            "readonly": "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {u};",
            "readwrite": "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {u};",
            "admin": "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {u};",
        }
        ddl = (
            f"CREATE USER {u} WITH PASSWORD '{p}';\n"
            f"{grants.get(role, grants['readwrite']).format(u=u)}\n"
            f"-- Solo visual (sin ejecutar)\n"
        )

        self.preview.delete("1.0", "end")
        self.preview.insert("1.0", ddl)

    def _ok(self):
        self.result_sql = self.preview.get("1.0", "end").strip()
        self.destroy()

    def _cancel(self):
        self.result_sql = None
        self.destroy()

    def _center(self, master):
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class AddFieldDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Agregar Campo")
        self.resizable(False, False)
        self.configure(bg=master.COL_BG)
        self.transient(master)
        self.grab_set()

        self.result = None

        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self, style="Panel.TFrame")
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        self.var_name = tk.StringVar(value="campo")
        self.var_type = tk.StringVar(value="VARCHAR(50)")
        self.var_pk = tk.BooleanVar(value=False)
        self.var_null = tk.BooleanVar(value=True)

        ttk.Label(frm, text="Nombre:", style="Small.TLabel").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_name, width=32).grid(row=0, column=1, **pad)

        ttk.Label(frm, text="Tipo:", style="Small.TLabel").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.var_type, width=32).grid(row=1, column=1, **pad)

        ttk.Checkbutton(frm, text="Primary Key (PK)", variable=self.var_pk).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 2))
        ttk.Checkbutton(frm, text="Permitir NULL", variable=self.var_null).grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 8))

        btns = ttk.Frame(frm, style="Panel.TFrame")
        btns.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(6, 6))
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)

        ttk.Button(btns, text="Cancelar", command=self._cancel).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(btns, text="Agregar", style="Ok.TButton", command=self._ok).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.bind("<Escape>", lambda *_: self._cancel())
        self.bind("<Return>", lambda *_: self._ok())
        self._center(master)

    def _ok(self):
        name = self.var_name.get().strip() or "campo"
        ctype = self.var_type.get().strip() or "VARCHAR(50)"
        pk = "✓" if self.var_pk.get() else ""
        null = "SI" if self.var_null.get() else "NO"
        self.result = (name, ctype, pk, null)
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    def _center(self, master):
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

# APP PRINCIPAL 
class DBManagerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DB Manager - Sistema de Gestión de Bases de Datos")
        self.geometry("1100x650")
        self.minsize(980, 600)

        # Colores
        self.COL_BG = "#1f2a36"
        self.COL_PANEL = "#223243"
        self.COL_PANEL2 = "#1f2b38"
        self.COL_TEXT = "#e8eef5"
        self.COL_ACCENT = "#2d78ff"
        self.COL_OK = "#1fbf75"
        self.COL_DANGER = "#ff4d4d"

        style = ttk.Style(self)
        for theme in ("clam", "alt", "default"):
            try:
                style.theme_use(theme)
                break
            except tk.TclError:
                pass
        self._apply_style(style)

        self.configure(bg=self.COL_BG)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Demo connections (en memoria)
        self.connections = [
            {"name": "postgres", "host": "localhost", "port": 5432, "database": "postgres", "user": "postgres", "sslmode": "disable"},
            {"name": "cockroach", "host": "localhost", "port": 26257, "database": "defaultdb", "user": "root", "sslmode": "disable"},
        ]

        self._build_header()
        self._build_content()

    def _apply_style(self, style: ttk.Style):
        style.configure("TFrame", background=self.COL_BG)
        style.configure("Panel.TFrame", background=self.COL_PANEL)
        style.configure("Panel2.TFrame", background=self.COL_PANEL2)

        style.configure("TLabel", background=self.COL_BG, foreground=self.COL_TEXT)
        style.configure("Header.TLabel", background=self.COL_BG, foreground=self.COL_TEXT, font=("Segoe UI", 14, "bold"))
        style.configure("Small.TLabel", background=self.COL_BG, foreground=self.COL_TEXT, font=("Segoe UI", 9))

        style.configure("TButton", font=("Segoe UI", 9), padding=8)
        style.configure("Primary.TButton", background=self.COL_ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", "#1f60d6")], foreground=[("active", "white")])

        style.configure("Ok.TButton", background=self.COL_OK, foreground="white")
        style.map("Ok.TButton", background=[("active", "#16925a")], foreground=[("active", "white")])

        style.configure("Danger.TButton", background=self.COL_DANGER, foreground="white")
        style.map("Danger.TButton", background=[("active", "#d83a3a")], foreground=[("active", "white")])

        style.configure("TNotebook", background=self.COL_BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 8), font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.COL_PANEL)], foreground=[("selected", "white")])

        style.configure("Treeview",
                        background=self.COL_PANEL2,
                        fieldbackground=self.COL_PANEL2,
                        foreground=self.COL_TEXT,
                        rowheight=24,
                        borderwidth=0)
        style.map("Treeview", background=[("selected", "#2a5ea8")])
        style.configure("TEntry", padding=6)

    # Header 
    def _build_header(self):
        header = ttk.Frame(self, style="Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ttk.Label(header, text="DB Manager", style="Header.TLabel").grid(row=0, column=0, padx=16, pady=10, sticky="w")
        self.status_label = ttk.Label(header, text="● Desconectado", style="Small.TLabel")
        self.status_label.grid(row=0, column=2, padx=16, sticky="e")

    # Content
    def _build_content(self):
        content = ttk.Frame(self, style="TFrame")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        self._build_left_sidebar(content)
        self._build_main_area(content)

    # Sidebar 
    def _build_left_sidebar(self, parent):
        left = ttk.Frame(parent, style="Panel.TFrame", width=260)
        left.grid(row=0, column=0, sticky="nsw")
        left.grid_propagate(False)
        left.grid_rowconfigure(1, weight=1)

        ttk.Label(left, text="Conexiones Guardadas", style="Small.TLabel").grid(
            row=0, column=0, padx=14, pady=(12, 6), sticky="w"
        )

        list_frame = ttk.Frame(left, style="Panel2.TFrame")
        list_frame.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.conn_list = tk.Listbox(
            list_frame,
            bg=self.COL_PANEL2,
            fg=self.COL_TEXT,
            selectbackground="#2a5ea8",
            highlightthickness=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        self.conn_list.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.conn_list.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.conn_list.configure(yscrollcommand=sb.set)

        self._refresh_conn_list()
        self.conn_list.selection_set(0)

        btns = ttk.Frame(left, style="Panel.TFrame")
        btns.grid(row=2, column=0, padx=12, pady=10, sticky="ew")
        btns.grid_columnconfigure(0, weight=1)

        ttk.Button(btns, text="Conectar", style="Primary.TButton", command=self.on_connect)\
            .grid(row=0, column=0, sticky="ew", pady=4)

        ttk.Button(btns, text="Crear Usuario", style="Ok.TButton", command=self.on_create_user)\
            .grid(row=1, column=0, sticky="ew", pady=4)

        ttk.Button(btns, text="Modificar", command=self.on_modify_connection)\
            .grid(row=2, column=0, sticky="ew", pady=4)

        ttk.Button(btns, text="Eliminar", style="Danger.TButton", command=self.on_delete_connection)\
            .grid(row=3, column=0, sticky="ew", pady=4)

        ttk.Label(left, text="DB Manager v1.0 | Sin DB", style="Small.TLabel")\
            .grid(row=3, column=0, padx=12, pady=(0, 10), sticky="w")

    def _refresh_conn_list(self):
        self.conn_list.delete(0, "end")
        for c in self.connections:
            self.conn_list.insert("end", c["name"])

    # Main area
    def _build_main_area(self, parent):
        main = ttk.Frame(parent, style="TFrame")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        nb = ttk.Notebook(main)
        nb.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        tab_tablas = ttk.Frame(nb, style="TFrame")
        tab_vistas = ttk.Frame(nb, style="TFrame")
        tab_proc = ttk.Frame(nb, style="TFrame")
        tab_trig = ttk.Frame(nb, style="TFrame")

        nb.add(tab_tablas, text="Tablas")
        nb.add(tab_vistas, text="Vistas")
        nb.add(tab_proc, text="Procedimientos")
        nb.add(tab_trig, text="Triggers")

        self._build_tablas(tab_tablas)
        self._build_object_editor(tab_vistas, kind="view", title="Gestión de Vistas",
                                  demo_items=["vw_resumen"])
        self._build_object_editor(tab_proc, kind="proc", title="Gestión de Procedimientos",
                                  demo_items=["sp_balance_mensual"])
        self._build_object_editor(tab_trig, kind="trigger", title="Gestión de Triggers",
                                  demo_items=["trg_audit_insert"])

    # TABLAS 
    def _build_tablas(self, tab):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        panel = ttk.Frame(tab, style="Panel.TFrame")
        panel.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        ttk.Label(panel, text="Gestión de Tablas", style="Header.TLabel").grid(
            row=0, column=0, padx=14, pady=(12, 8), sticky="w"
        )

        name_row = ttk.Frame(panel, style="Panel.TFrame")
        name_row.grid(row=1, column=0, sticky="ew", padx=14)
        name_row.grid_columnconfigure(1, weight=1)

        ttk.Label(name_row, text="Nombre de la tabla:", style="Small.TLabel").grid(row=0, column=0, sticky="w")
        self.table_name_var = tk.StringVar(value="mi_tabla")
        ttk.Entry(name_row, textvariable=self.table_name_var).grid(row=0, column=1, sticky="ew", padx=(10, 0))

        body = ttk.Frame(panel, style="Panel.TFrame")
        body.grid(row=2, column=0, sticky="nsew", padx=14, pady=10)
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)

        # Campos 
        ttk.Label(body, text="Campos:", style="Small.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        fields_frame = ttk.Frame(body, style="Panel2.TFrame")
        fields_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        fields_frame.grid_rowconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(0, weight=1)

        cols = ("nombre", "tipo", "pk", "null")
        self.fields_tree = ttk.Treeview(fields_frame, columns=cols, show="headings", selectmode="browse")
        for c, h in [("nombre", "Nombre"), ("tipo", "Tipo"), ("pk", "PK"), ("null", "NULL")]:
            self.fields_tree.heading(c, text=h)
        self.fields_tree.column("nombre", width=140, anchor="w")
        self.fields_tree.column("tipo", width=120, anchor="w")
        self.fields_tree.column("pk", width=40, anchor="center")
        self.fields_tree.column("null", width=60, anchor="center")
        self.fields_tree.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        sb = ttk.Scrollbar(fields_frame, orient="vertical", command=self.fields_tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.fields_tree.configure(yscrollcommand=sb.set)

        self.fields_tree.insert("", "end", values=("id", "INT", "✓", "NO"))

        # Botones campos
        fields_btns = ttk.Frame(body, style="Panel.TFrame")
        fields_btns.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(fields_btns, text="+ Agregar Campo", style="Ok.TButton", command=self.on_add_field)\
            .grid(row=0, column=0, padx=(0, 8))
        ttk.Button(fields_btns, text="Eliminar Campo", command=self.on_delete_field)\
            .grid(row=0, column=1, padx=(0, 8))
        ttk.Button(fields_btns, text="Limpiar", command=self.on_clear_fields)\
            .grid(row=0, column=2)

        # SQL generado
        ttk.Label(body, text="SQL Generado:", style="Small.TLabel").grid(row=0, column=1, sticky="w", pady=(0, 6))
        self.sql_text_tablas = self._make_sql_editor(body, row=1, col=1)

        self.table_name_var.trace_add("write", lambda *_: self.refresh_table_sql())
        self.refresh_table_sql()

        # Barra inferior
        bottom = self._make_bottom_bar(panel,
                                       create_cb=self.on_create_table,
                                       gen_cb=self.refresh_table_sql,
                                       list_cb=self.on_list_tables_demo,
                                       load_cb=self.on_load_table_demo,
                                       mod_cb=self.on_modify_table_demo,
                                       del_cb=self.on_delete_table_demo)
        bottom.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 12))

    def on_add_field(self):
        dlg = AddFieldDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.fields_tree.insert("", "end", values=dlg.result)
            self.refresh_table_sql()

    def on_delete_field(self):
        sel = self.fields_tree.selection()
        if not sel:
            messagebox.showwarning("Campos", "Selecciona un campo para eliminar.")
            return
        self.fields_tree.delete(sel[0])
        self.refresh_table_sql()

    def on_clear_fields(self):
        for iid in self.fields_tree.get_children():
            self.fields_tree.delete(iid)
        self.refresh_table_sql()

    def refresh_table_sql(self):
        table = (self.table_name_var.get().strip() or "mi_tabla")
        fields = []
        pk_cols = []

        for iid in self.fields_tree.get_children():
            nombre, tipo, pk, null = self.fields_tree.item(iid, "values")
            is_pk = (pk == "✓")
            is_null = (null == "SI")
            col = f"  {nombre} {tipo}"
            if not is_null:
                col += " NOT NULL"
            fields.append(col)
            if is_pk:
                pk_cols.append(nombre)

        if not fields:
            ddl = f"CREATE TABLE {table} (\n  -- define campos...\n);\n"
        else:
            if pk_cols:
                fields.append(f"  PRIMARY KEY ({', '.join(pk_cols)})")
            ddl = f"CREATE TABLE {table} (\n" + ",\n".join(fields) + "\n);\n"

        self._set_text(self.sql_text_tablas, ddl)

    # Acciones demo de tabla
    def on_create_table(self):
        ddl = self.sql_text_tablas.get("1.0", "end").strip()
        messagebox.showinfo("Crear Tabla (demo)", "Acción simulada.\n\nSQL:\n" + ddl[:900])

    def on_list_tables_demo(self):
        messagebox.showinfo("Listar (demo)", "Listando tablas de ejemplo (sin DB).")

    def on_load_table_demo(self):
        self.table_name_var.set("usuarios")
        self.on_clear_fields()
        self.fields_tree.insert("", "end", values=("id_usuario", "INT", "✓", "NO"))
        self.fields_tree.insert("", "end", values=("email", "VARCHAR(120)", "", "NO"))
        self.refresh_table_sql()

    def on_modify_table_demo(self):
        messagebox.showinfo("Modificar (demo)", "Acción simulada (sin DB).")

    def on_delete_table_demo(self):
        messagebox.showwarning("Eliminar (demo)", "Acción simulada (sin DB).")

    # VISTAS / PROCS / TRIGGERS
    def _build_object_editor(self, tab, kind: str, title: str, demo_items):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        panel = ttk.Frame(tab, style="Panel.TFrame")
        panel.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        ttk.Label(panel, text=title, style="Header.TLabel").grid(row=0, column=0, padx=14, pady=(12, 8), sticky="w")

        name_row = ttk.Frame(panel, style="Panel.TFrame")
        name_row.grid(row=1, column=0, sticky="ew", padx=14)
        name_row.grid_columnconfigure(1, weight=1)

        ttk.Label(name_row, text="Nombre:", style="Small.TLabel").grid(row=0, column=0, sticky="w")
        name_var = tk.StringVar(value=demo_items[0] if demo_items else "")
        ttk.Entry(name_row, textvariable=name_var).grid(row=0, column=1, sticky="ew", padx=(10, 0))

        body = ttk.Frame(panel, style="Panel.TFrame")
        body.grid(row=2, column=0, sticky="nsew", padx=14, pady=10)
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)

        ttk.Label(body, text="Lista:", style="Small.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        list_tree = self._make_list_tree(body, row=1, col=0)

        for n in demo_items[:2]:
            list_tree.insert("", "end", values=(n,))

        ttk.Label(body, text="SQL:", style="Small.TLabel").grid(row=0, column=1, sticky="w", pady=(0, 6))
        sql_text = self._make_sql_editor(body, row=1, col=1)

        # SQL demo por tipo
        if kind == "view":
            sql_text.insert("1.0", f"CREATE OR REPLACE VIEW {name_var.get()} AS\nSELECT * FROM usuarios;\n")
        elif kind == "proc":
            sql_text.insert("1.0", f"CREATE OR REPLACE PROCEDURE {name_var.get()}()\nLANGUAGE plpgsql\nAS $$\nBEGIN\n  -- ...\nEND;\n$$;\n")
        else:
            sql_text.insert("1.0",
                            f"CREATE OR REPLACE FUNCTION fn_{name_var.get()}()\nRETURNS trigger AS $$\nBEGIN\n  RETURN NEW;\nEND;\n$$ LANGUAGE plpgsql;\n\n"
                            f"CREATE TRIGGER {name_var.get()}\nBEFORE INSERT ON mi_tabla\nFOR EACH ROW EXECUTE FUNCTION fn_{name_var.get()}();\n")

        def refresh_sql_preview():
            n = name_var.get().strip() or "objeto"
            if kind == "view":
                self._set_text(sql_text, f"CREATE OR REPLACE VIEW {n} AS\nSELECT * FROM usuarios;\n")
            elif kind == "proc":
                self._set_text(sql_text, f"CREATE OR REPLACE PROCEDURE {n}()\nLANGUAGE plpgsql\nAS $$\nBEGIN\n  -- ...\nEND;\n$$;\n")
            else:
                self._set_text(sql_text,
                               f"CREATE OR REPLACE FUNCTION fn_{n}()\nRETURNS trigger AS $$\nBEGIN\n  RETURN NEW;\nEND;\n$$ LANGUAGE plpgsql;\n\n"
                               f"CREATE TRIGGER {n}\nBEFORE INSERT ON mi_tabla\nFOR EACH ROW EXECUTE FUNCTION fn_{n}();\n")

        name_var.trace_add("write", lambda *_: refresh_sql_preview())

        def on_list():
            for iid in list_tree.get_children():
                list_tree.delete(iid)
            for n in demo_items[:2]:
                list_tree.insert("", "end", values=(n,))

        def on_load():
            sel = list_tree.selection()
            if not sel:
                messagebox.showwarning("Cargar", "Selecciona un item de la lista.")
                return
            value = list_tree.item(sel[0], "values")[0]
            name_var.set(value)

        def on_create():
            messagebox.showinfo("Crear (demo)", "Acción simulada (sin DB).")

        def on_modify():
            messagebox.showinfo("Modificar (demo)", "Acción simulada (sin DB).")

        def on_delete():
            sel = list_tree.selection()
            if not sel:
                messagebox.showwarning("Eliminar", "Selecciona un item para eliminar de la lista (demo).")
                return
            list_tree.delete(sel[0])

        bottom = self._make_bottom_bar(panel,
                                       create_cb=on_create,
                                       gen_cb=refresh_sql_preview,
                                       list_cb=on_list,
                                       load_cb=on_load,
                                       mod_cb=on_modify,
                                       del_cb=on_delete)
        bottom.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 12))

    # Reusables
    def _make_sql_editor(self, parent, row, col):
        frame = ttk.Frame(parent, style="Panel2.TFrame")
        frame.grid(row=row, column=col, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        text = tk.Text(frame, bg=self.COL_PANEL2, fg=self.COL_TEXT,
                       insertbackground=self.COL_TEXT, relief="flat",
                       font=("Consolas", 10), wrap="none")
        text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        sb = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        sb.grid(row=0, column=1, sticky="ns")
        text.configure(yscrollcommand=sb.set)
        return text

    def _make_list_tree(self, parent, row, col):
        frame = ttk.Frame(parent, style="Panel2.TFrame")
        frame.grid(row=row, column=col, sticky="nsew", padx=(0, 10))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(frame, columns=("nombre",), show="headings", selectmode="browse")
        tree.heading("nombre", text="Nombre")
        tree.column("nombre", width=240, anchor="w")
        tree.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=sb.set)
        return tree

    def _make_bottom_bar(self, parent, create_cb, gen_cb, list_cb, load_cb, mod_cb, del_cb):
        bottom = ttk.Frame(parent, style="Panel.TFrame")
        for i in range(6):
            bottom.grid_columnconfigure(i, weight=1)

        ttk.Button(bottom, text="Crear", style="Primary.TButton", command=create_cb).grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(bottom, text="Generar DDL", command=gen_cb).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(bottom, text="Listar", command=list_cb).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(bottom, text="Cargar", command=load_cb).grid(row=0, column=3, sticky="ew", padx=4)
        ttk.Button(bottom, text="Modificar", command=mod_cb).grid(row=0, column=4, sticky="ew", padx=4)
        ttk.Button(bottom, text="Eliminar", style="Danger.TButton", command=del_cb).grid(row=0, column=5, sticky="ew", padx=4)
        return bottom

    def _set_text(self, text_widget: tk.Text, value: str):
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", value)

    # Sidebar actions
    def _get_selected_conn_index(self):
        sel = self.conn_list.curselection()
        return sel[0] if sel else None

    def on_connect(self):
        idx = self._get_selected_conn_index()
        name = self.connections[idx]["name"] if idx is not None else "demo"
        self.status_label.configure(text=f"● Conectado (demo): {name}")

    def on_create_user(self):
        dlg = UserDialog(self)
        self.wait_window(dlg)
        if dlg.result_sql:
            messagebox.showinfo("SQL (demo)", "SQL generado (no ejecutado).")

    def on_modify_connection(self):
        idx = self._get_selected_conn_index()
        if idx is None:
            messagebox.showwarning("Modificar", "Selecciona una conexión.")
            return
        dlg = ConnectionDialog(self, "Modificar Conexión", initial=self.connections[idx])
        self.wait_window(dlg)
        if dlg.result:
            self.connections[idx] = dlg.result
            self._refresh_conn_list()
            self.conn_list.selection_set(idx)

    def on_delete_connection(self):
        idx = self._get_selected_conn_index()
        if idx is None:
            messagebox.showwarning("Eliminar", "Selecciona una conexión.")
            return
        self.connections.pop(idx)
        self._refresh_conn_list()
        if self.connections:
            self.conn_list.selection_set(min(idx, len(self.connections) - 1))


if __name__ == "__main__":
    DBManagerUI().mainloop()
