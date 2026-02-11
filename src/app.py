import tkinter as tk
from tkinter import ttk, messagebox
import time
from datetime import datetime

# Tus imports (si ya los tenés)
from db.init_db import init_db
from db.connection import get_connection

init_db()


class QueryTab:
    def __init__(self, name: str, query: str = ""):
        self.name = name
        self.query = query
        self.results = None
        self.execution_time = 0
        self.rows_affected = 0
        self.created_at = datetime.now()


class DBManagerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Database Manager - Query Viewer")
        self.geometry("1400x800")
        self.minsize(1200, 700)

        self.COL_BG = "#0f172a" # fondo general
        self.COL_PANEL = "#111c2f" # paneles
        self.COL_PANEL2 = "#0b1220" # más oscuro (editor)
        self.COL_STROKE = "#22324a" # bordes
        self.COL_TEXT = "#e5e7eb"
        self.COL_MUTED = "#93a4b8"
        self.COL_ACCENT = "#3b82f6" # azul botón ejecutar
        self.COL_OK = "#22c55e"
        self.COL_DANGER = "#ef4444"
        self.COL_TAB_ACTIVE = "#162742"
        self.COL_TAB_INACTIVE = "#0b1220"

        self.connected = False
        self.conn_name = "cockroach"
        self.conn = None
        self.theme_mode = "dark"  # dark o light
    
        self.tabs = {}
        self.current_tab = None
        self.tab_counter = 0
        
        self.section_expanded = {"table": True, "view": True, "proc": True, "func": True, "trigger": True}
        self.sidebar_search = ""

        self.configure(bg=self.COL_BG)
        self._apply_style()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_layout()

        self._new_tab()

        self.bind("<F5>", lambda *_: self.on_execute())
        self.bind("<Control-t>", lambda *_: self._new_tab())
        self.bind("<Control-w>", lambda *_: self._close_current_tab())

    def _apply_style(self):
        style = ttk.Style(self)
        for theme in ("clam", "alt", "default"):
            try:
                style.theme_use(theme)
                break
            except tk.TclError:
                pass

        style.configure("TFrame", background=self.COL_BG)
        style.configure("Panel.TFrame", background=self.COL_PANEL)
        style.configure("Editor.TFrame", background=self.COL_PANEL2)
        style.configure("TLabel", background=self.COL_BG, foreground=self.COL_TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=self.COL_BG, foreground=self.COL_MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=self.COL_BG, foreground=self.COL_TEXT, font=("Segoe UI", 13, "bold"))

        style.configure("TButton", font=("Segoe UI", 9), padding=(10, 7))
        style.configure("Primary.TButton", background=self.COL_ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", "#2563eb")])

        style.configure("Ghost.TButton", background=self.COL_PANEL, foreground=self.COL_TEXT, padding=(10, 7))
        style.map("Ghost.TButton", background=[("active", "#162742")])

        style.configure("Plus.TButton", background=self.COL_PANEL, foreground=self.COL_TEXT, padding=(8, 2))
        style.map("Plus.TButton", background=[("active", "#162742")])
        
        style.configure("Tab.TButton", background=self.COL_TAB_INACTIVE, foreground=self.COL_TEXT, padding=(10, 6), borderwidth=0)
        style.map("Tab.TButton", background=[("active", "#162742")])
        
        style.configure("Tab.Active.TButton", background=self.COL_TAB_ACTIVE, foreground=self.COL_ACCENT, padding=(10, 6), borderwidth=0)
        style.map("Tab.Active.TButton", background=[("active", "#162742")])

        style.configure("Treeview",
                        background=self.COL_PANEL,
                        fieldbackground=self.COL_PANEL,
                        foreground=self.COL_TEXT,
                        rowheight=26,
                        borderwidth=0,
                        relief="flat")
        style.map("Treeview", background=[("selected", "#1f3a68")])
        style.configure("Treeview.Heading",
                        background=self.COL_PANEL,
                        foreground=self.COL_MUTED,
                        relief="flat",
                        borderwidth=0)
        
        style.configure("Search.TEntry", background=self.COL_PANEL2, foreground=self.COL_TEXT, padding=5)
        style.map("Search.TEntry", fieldbackground=[("", self.COL_PANEL2)])
        
        style.configure("Stats.TLabel", background=self.COL_PANEL, foreground=self.COL_OK, font=("Consolas", 9))

    # Topbar
    def _build_topbar(self):
        top = ttk.Frame(self, style="Panel.TFrame")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(2, weight=1)

        left = ttk.Frame(top, style="Panel.TFrame")
        left.grid(row=0, column=0, sticky="w", padx=14, pady=10)

        ttk.Label(left, text="🗄️", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(left, text="Database Manager", style="Title.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 0))

        # Conexión actual
        self.lbl_conn = ttk.Label(top, text=f"{self.conn_name} @ localhost", style="Muted.TLabel")
        self.lbl_conn.grid(row=0, column=1, sticky="w", padx=(8, 0))

        spacer = ttk.Frame(top, style="Panel.TFrame")
        spacer.grid(row=0, column=2, sticky="ew")
        right = ttk.Frame(top, style="Panel.TFrame")
        right.grid(row=0, column=3, sticky="e", padx=14)

        ttk.Button(right, text="Conectar", style="Ghost.TButton", command=self.on_connect).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(right, text="🌓", style="Ghost.TButton", command=self.toggle_theme).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(right, text="⚙️", style="Ghost.TButton", command=self.on_settings).grid(row=0, column=2, padx=(0, 8))

        self.lbl_status = ttk.Label(right, text="● Desconectado", style="Muted.TLabel")
        self.lbl_status.grid(row=0, column=3, padx=(10, 0))

    def toggle_theme(self):
        """Cambia entre tema oscuro y claro"""
        if self.theme_mode == "dark":
            self._apply_light_theme()
            self.theme_mode = "light"
        else:
            self._apply_dark_theme()
            self.theme_mode = "dark"

    def _apply_dark_theme(self):
        """Aplica tema oscuro (por defecto)"""
        self.COL_BG = "#0f172a"
        self.COL_PANEL = "#111c2f"
        self.COL_PANEL2 = "#0b1220"
        self.COL_STROKE = "#22324a"
        self.COL_TEXT = "#e5e7eb"
        self.COL_MUTED = "#93a4b8"
        self.COL_ACCENT = "#3b82f6"
        self.COL_OK = "#22c55e"
        self.COL_DANGER = "#ef4444"
        self.COL_TAB_ACTIVE = "#162742"
        self.COL_TAB_INACTIVE = "#0b1220"
        
        self.configure(bg=self.COL_BG)
        self._reapply_colors()

    def _apply_light_theme(self):
        """Aplica tema claro"""
        self.COL_BG = "#f9fafb"
        self.COL_PANEL = "#f3f4f6"
        self.COL_PANEL2 = "#ffffff"
        self.COL_STROKE = "#e5e7eb"
        self.COL_TEXT = "#1f2937"
        self.COL_MUTED = "#6b7280"
        self.COL_ACCENT = "#2563eb"
        self.COL_OK = "#16a34a"
        self.COL_DANGER = "#dc2626"
        self.COL_TAB_ACTIVE = "#dbeafe"
        self.COL_TAB_INACTIVE = "#e5e7eb"
        
        self.configure(bg=self.COL_BG)
        self._reapply_colors()

    def _reapply_colors(self):
        """Reaplica los estilos con los nuevos colores"""
        style = ttk.Style(self)
        
        style.configure("TFrame", background=self.COL_BG)
        style.configure("Panel.TFrame", background=self.COL_PANEL)
        style.configure("Editor.TFrame", background=self.COL_PANEL2)
        style.configure("TLabel", background=self.COL_BG, foreground=self.COL_TEXT)
        style.configure("Muted.TLabel", background=self.COL_BG, foreground=self.COL_MUTED)
        style.configure("Title.TLabel", background=self.COL_BG, foreground=self.COL_TEXT)
        
        style.configure("Primary.TButton", background=self.COL_ACCENT, foreground="white")
        style.map("Primary.TButton", background=[("active", self.COL_ACCENT)])
        
        style.configure("Ghost.TButton", background=self.COL_PANEL, foreground=self.COL_TEXT)
        style.map("Ghost.TButton", background=[("active", self.COL_STROKE)])
        
        style.configure("Plus.TButton", background=self.COL_PANEL, foreground=self.COL_TEXT)
        style.map("Plus.TButton", background=[("active", self.COL_STROKE)])
        
        style.configure("Treeview",
                        background=self.COL_PANEL,
                        fieldbackground=self.COL_PANEL,
                        foreground=self.COL_TEXT)
        style.map("Treeview", background=[("selected", self.COL_ACCENT)])
        style.configure("Treeview.Heading",
                        background=self.COL_PANEL,
                        foreground=self.COL_MUTED)
        
        style.configure("Stats.TLabel", background=self.COL_PANEL, foreground=self.COL_OK)
        
        if hasattr(self, 'sql_text'):
            self.sql_text.configure(
                bg=self.COL_PANEL2,
                fg=self.COL_TEXT,
                insertbackground=self.COL_TEXT
            )
        
        if hasattr(self, 'sidebar_canvas'):
            self.sidebar_canvas.configure(bg=self.COL_PANEL)
            self.sidebar_inner.configure(style="Panel.TFrame")

    # Layout
    def _build_layout(self):
        root = ttk.Frame(self, style="TFrame")
        root.grid(row=1, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        self._build_sidebar(root)
        self._build_main(root)

    # Sidebar
    def _build_sidebar(self, parent):
        side = ttk.Frame(parent, style="Panel.TFrame", width=340)
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)
        side.grid_rowconfigure(2, weight=1)
        side.grid_columnconfigure(0, weight=1)

        # Header
        header = ttk.Frame(side, style="Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        ttk.Label(header, text="🔍 Explorador de Objetos", style="TLabel", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")

        # Search bar
        search_frame = ttk.Frame(side, style="Panel.TFrame")
        search_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        
        self.search_var = tk.StringVar()
        search_field = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=self.COL_PANEL2,
            fg=self.COL_TEXT,
            insertbackground=self.COL_TEXT,
            relief="flat",
            font=("Segoe UI", 9),
            width=30
        )
        search_field.pack(fill="x", ipady=5)
        search_field.insert(0, "Buscar objetos...")
        search_field.bind("<FocusIn>", lambda e: search_field.delete(0, "end") if search_field.get() == "Buscar objetos..." else None)
        search_field.bind("<FocusOut>", lambda e: search_field.insert(0, "Buscar objetos...") if search_field.get() == "" else None)
        search_field.bind("<KeyRelease>", self._on_search_change)

        # Treeview principal
        tree_frame = ttk.Frame(side, style="Panel.TFrame")
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=(), show="tree", height=30)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sections = {}

        tbl_item = self.tree.insert("", "end", text="📋 Tablas", open=True, tags=("section",))
        self.sections["table"] = tbl_item
        for it in ["users", "orders", "products", "customers"]:
            self.tree.insert(tbl_item, "end", text=it, tags=("item",))

        view_item = self.tree.insert("", "end", text="👁️ Vistas", open=True, tags=("section",))
        self.sections["view"] = view_item
        for it in ["active_users", "order_summary"]:
            self.tree.insert(view_item, "end", text=it, tags=("item",))

        proc_item = self.tree.insert("", "end", text="⚙️ Procedimientos", open=False, tags=("section",))
        self.sections["proc"] = proc_item
        for it in ["create_order", "update_stock"]:
            self.tree.insert(proc_item, "end", text=it, tags=("item",))

        func_item = self.tree.insert("", "end", text="∑ Funciones", open=False, tags=("section",))
        self.sections["func"] = func_item
        for it in ["calculate_tax", "get_discount"]:
            self.tree.insert(func_item, "end", text=it, tags=("item",))

        trigger_item = self.tree.insert("", "end", text="⚡ Triggers", open=False, tags=("section",))
        self.sections["trigger"] = trigger_item
        for it in ["trg_audit_insert"]:
            self.tree.insert(trigger_item, "end", text=it, tags=("item",))

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        ttk.Label(side, text="💡 Ctrl+T: Nueva query | Ctrl+W: Cerrar", style="Muted.TLabel")\
            .grid(row=3, column=0, sticky="w", padx=12, pady=(0, 12))

    def _on_tree_select(self, event):
        """Cuando selecciona un item del árbol"""
        sel = self.tree.selection()
        if not sel:
            return
        
        item_id = sel[0]
        item_text = self.tree.item(item_id, "text")
        is_section = "section" in self.tree.item(item_id, "tags")
        if is_section:
            return
        
        parent_id = self.tree.parent(item_id)
        if parent_id in self.sections.values():
            kind = None
            for k, v in self.sections.items():
                if v == parent_id:
                    kind = k
                    break
            
            if kind:
                if kind == "table":
                    self._set_sql(f"SELECT * FROM {item_text} LIMIT 50;")
                elif kind == "view":
                    self._set_sql(f"SELECT * FROM {item_text} LIMIT 50;")
                elif kind == "proc":
                    self._set_sql(f"-- CALL {item_text}(...);")
                elif kind == "func":
                    self._set_sql(f"-- SELECT {item_text}(...);")
                else:
                    self._set_sql(f"-- Trigger: {item_text}")

    def _on_search_change(self, _):
        search_term = self.search_var.get().lower()
        if search_term == "buscar objetos...":
            search_term = ""
        
        self.tree.delete(*self.tree.get_children())
        
        items_data = {
            "table": ("📋 Tablas", ["users", "orders", "products", "customers"]),
            "view": ("👁️ Vistas", ["active_users", "order_summary"]),
            "proc": ("⚙️ Procedimientos", ["create_order", "update_stock"]),
            "func": ("∑ Funciones", ["calculate_tax", "get_discount"]),
            "trigger": ("⚡ Triggers", ["trg_audit_insert"]),
        }
        
        for kind, (title, items) in items_data.items():
            filtered_items = [i for i in items if search_term in i.lower()] if search_term else items
            if filtered_items or not search_term:
                parent = self.tree.insert("", "end", text=title, open=True, tags=("section",))
                self.sections[kind] = parent
                for item in filtered_items:
                    self.tree.insert(parent, "end", text=item, tags=("item",))

    # SQL editor + Results
    def _build_main(self, parent):
        main = ttk.Frame(parent, style="TFrame")
        main.grid(row=0, column=1, sticky="nsew", padx=12, pady=12)
        main.grid_rowconfigure(2, weight=1)
        main.grid_rowconfigure(4, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Tabs header
        tabs_frame = ttk.Frame(main, style="Panel.TFrame")
        tabs_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        tabs_frame.grid_columnconfigure(0, weight=1)
        
        self.tabs_container = ttk.Frame(tabs_frame, style="Panel.TFrame")
        self.tabs_container.grid(row=0, column=0, sticky="w")
        
        tabs_actions = ttk.Frame(tabs_frame, style="Panel.TFrame")
        tabs_actions.grid(row=0, column=1, sticky="e")
        ttk.Button(tabs_actions, text="➕ Nueva Query (Ctrl+T)", style="Ghost.TButton", 
                   command=self._new_tab).pack(side="left", padx=(0, 6))

        # Editor header
        editor_head = ttk.Frame(main, style="Panel.TFrame")
        editor_head.grid(row=1, column=0, sticky="ew")
        editor_head.grid_columnconfigure(0, weight=1)

        ttk.Label(editor_head, text="📝 Editor SQL", style="TLabel", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=10)

        btns = ttk.Frame(editor_head, style="Panel.TFrame")
        btns.grid(row=0, column=1, sticky="e", padx=12)

        ttk.Button(btns, text="▶ Ejecutar (F5)", style="Primary.TButton", command=self.on_execute).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="💾", style="Ghost.TButton", command=self.on_save_sql).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(btns, text="🗑", style="Ghost.TButton", command=self.on_clear_sql).grid(row=0, column=2)

        # SQL editor
        editor_wrap = ttk.Frame(main, style="Editor.TFrame")
        editor_wrap.grid(row=2, column=0, sticky="nsew")
        editor_wrap.grid_rowconfigure(0, weight=1)
        editor_wrap.grid_columnconfigure(0, weight=1)

        self.sql_text = tk.Text(
            editor_wrap,
            bg=self.COL_PANEL2,
            fg=self.COL_TEXT,
            insertbackground=self.COL_TEXT,
            relief="flat",
            font=("Consolas", 11),
            wrap="none",
            padx=12,
            pady=10
        )
        self.sql_text.grid(row=0, column=0, sticky="nsew")
        self.sql_text.insert("1.0", "-- Escribe tu consulta SQL aquí\nSELECT * FROM users LIMIT 10;\n")

        vsb = ttk.Scrollbar(editor_wrap, orient="vertical", command=self.sql_text.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.sql_text.configure(yscrollcommand=vsb.set)

        results_head = ttk.Frame(main, style="Panel.TFrame")
        results_head.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        
        ttk.Label(results_head, text="📊 Resultados", style="TLabel", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=10)
        
        self.stats_frame = ttk.Frame(results_head, style="Panel.TFrame")
        self.stats_frame.grid(row=0, column=1, sticky="e", padx=12)
        results_wrap = ttk.Frame(main, style="Panel.TFrame")
        results_wrap.grid(row=4, column=0, sticky="nsew")
        results_wrap.grid_rowconfigure(0, weight=1)
        results_wrap.grid_columnconfigure(0, weight=1)

        self.results = ttk.Treeview(results_wrap, columns=(), show="headings")
        self.results.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        vsb = ttk.Scrollbar(results_wrap, orient="vertical", command=self.results.yview)
        vsb.grid(row=0, column=1, sticky="ns", pady=12)
        self.results.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(results_wrap, orient="horizontal", command=self.results.xview)
        hsb.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.results.configure(xscrollcommand=hsb.set)

        self._set_empty_results("No hay resultados para mostrar")

    def _update_tabs_ui(self):
        """Redibuja los tabs"""
        for widget in self.tabs_container.winfo_children():
            widget.destroy()
        
        for tab_id, tab_obj in self.tabs.items():
            is_active = tab_id == self.current_tab
            style = "Tab.Active.TButton" if is_active else "Tab.TButton"
            
            btn = ttk.Button(
                self.tabs_container,
                text=f"{tab_obj.name} {'●' if is_active else ''} ",
                style=style,
                command=lambda tid=tab_id: self._switch_tab(tid)
            )
            btn.pack(side="left", padx=(0, 2))

    def _new_tab(self, query=""):
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"
        tab_obj = QueryTab(f"Query {self.tab_counter}", query)
        self.tabs[tab_id] = tab_obj
        self.current_tab = tab_id
        self._switch_tab(tab_id)

    def _switch_tab(self, tab_id: str):
        """Cambia a una pestaña específica y carga su contenido"""
        if tab_id not in self.tabs:
            return
        
        self.current_tab = tab_id
        tab_obj = self.tabs[tab_id]

        for tid, tobj in self.tabs.items():
            if tid != tab_id:
                tobj.query = self.sql_text.get("1.0", "end").strip()
        
        self.sql_text.delete("1.0", "end")
        self.sql_text.insert("1.0", tab_obj.query)
        
        self._update_tabs_ui()

    def _close_current_tab(self):
        """Cierra la pestaña actual"""
        if len(self.tabs) <= 1:
            return
        
        tab_id = self.current_tab
        del self.tabs[tab_id]
        
        if self.tabs:
            self.current_tab = next(iter(self.tabs.keys()))
            self._switch_tab(self.current_tab)
        
        self._update_tabs_ui()

    # Behaviors
    def open_create_object(self, kind: str):
        labels = {
            "table": "Crear Tabla",
            "view": "Crear Vista",
            "proc": "Crear Procedimiento",
            "func": "Crear Función",
            "trigger": "Crear Trigger",
        }
        messagebox.showinfo("Nuevo objeto", f"{labels.get(kind, 'Crear')} (pantalla pendiente)\n\nAquí vas a navegar a tu pantalla de creación.")

    def on_select_object(self, kind: str, tree: ttk.Treeview):
        sel = tree.selection()
        if not sel:
            return
        name = tree.item(sel[0], "text")
        if kind == "table":
            self._set_sql(f"SELECT * FROM {name} LIMIT 50;")
        elif kind == "view":
            self._set_sql(f"SELECT * FROM {name} LIMIT 50;")
        elif kind == "proc":
            self._set_sql(f"-- CALL {name}(...);")
        elif kind == "func":
            self._set_sql(f"-- SELECT {name}(...);")
        else:
            self._set_sql(f"-- Trigger: {name}")

    def on_connect(self):
        try:
            self.conn = get_connection()
            self.connected = True
            self.lbl_status.configure(text="● Conectado", foreground=self.COL_OK)
            self.refresh_object_explorer()
        except Exception as e:
            self.connected = False
            self.conn = None
            self.lbl_status.configure(text="● Desconectado", foreground=self.COL_MUTED)
            messagebox.showerror("Conexión", f"No se pudo conectar.\n\n{e}")

    def on_settings(self):
        messagebox.showinfo("Settings", "Luego aquí metemos conexiones.json y el modal de conexiones.")

    def on_execute(self):
        sql = self.sql_text.get("1.0", "end").strip()
        if not sql:
            return

        if not self.connected or not self.conn:
            self._set_empty_results("Conéctate para ejecutar consultas")
            return

        try:
            start_time = time.time()
            with self.conn.cursor() as cur:
                cur.execute(sql)

                if cur.description:
                    cols = [d[0] for d in cur.description]
                    rows = cur.fetchall()
                    execution_time = time.time() - start_time
                    self._fill_results(cols, rows, execution_time, len(rows))
                else:
                    self.conn.commit()
                    execution_time = time.time() - start_time
                    self._set_empty_results(f"✓ Consulta ejecutada ({execution_time:.3f}s)")
        except Exception as e:
            self._set_empty_results("❌ Error al ejecutar")
            messagebox.showerror("SQL Error", str(e))

    def on_save_sql(self):
        messagebox.showinfo("Guardar", "Luego guardamos historial / archivos .sql.")

    def on_clear_sql(self):
        self.sql_text.delete("1.0", "end")

    # pg_catalog)
    def refresh_object_explorer(self):
        if not self.connected or not self.conn:
            return

        try:
            tables = self._fetch_tables()
            views = self._fetch_views()
            functions = self._fetch_functions()
            triggers = self._fetch_triggers()
            
            self._update_tree_section("table", tables)
            self._update_tree_section("view", views)
            self._update_tree_section("func", functions)
            self._update_tree_section("trigger", triggers)

        except Exception as e:
            messagebox.showwarning(
                "Explorador de Objetos",
                f"No se pudieron cargar los objetos.\n\n{e}"
            )

    def _update_tree_section(self, kind: str, items: list[str]):
        """Actualiza una sección del árbol con nuevos items"""
        parent_id = self.sections.get(kind)
        if not parent_id:
            return
        
        for iid in self.tree.get_children(parent_id):
            self.tree.delete(iid)
        
        for item in items:
            self.tree.insert(parent_id, "end", text=item, tags=("item",))

    def _fetch_tables(self):
        sql = """
            SELECT c.relname
            FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'r'
            ORDER BY c.relname;
        """
        return self._fetch_single_col(sql)

    def _fetch_views(self):
        sql = """
            SELECT c.relname
            FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'v'
            ORDER BY c.relname;
        """
        return self._fetch_single_col(sql)

    def _fetch_functions(self):
        sql = """
            SELECT p.proname
            FROM pg_catalog.pg_proc p
            JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = 'public'
            ORDER BY p.proname;
        """
        return self._fetch_single_col(sql)

    def _fetch_triggers(self):
        sql = """
            SELECT tg.tgname
            FROM pg_catalog.pg_trigger tg
            JOIN pg_catalog.pg_class c ON c.oid = tg.tgrelid
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND NOT tg.tgisinternal
            ORDER BY tg.tgname;
        """
        return self._fetch_single_col(sql)

    def _fetch_single_col(self, sql):
        with self.conn.cursor() as cur:
            cur.execute(sql)
            return [row[0] for row in cur.fetchall()]

    # Helpers
    def _set_sql(self, s: str):
        self.sql_text.delete("1.0", "end")
        self.sql_text.insert("1.0", s + "\n")

    def _set_empty_results(self, msg: str):
        for c in self.results["columns"]:
            self.results.heading(c, text="")
            self.results.column(c, width=0)
        self.results["columns"] = ("_msg",)
        self.results.heading("_msg", text="")
        self.results.column("_msg", width=800, anchor="w")
        self.results.delete(*self.results.get_children())
        self.results.insert("", "end", values=(msg,))
        
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

    def _fill_results(self, cols, rows, execution_time=0, row_count=0):
        self.results.delete(*self.results.get_children())
        self.results["columns"] = cols
        
        for c in cols:
            self.results.heading(c, text=c)
            self.results.column(c, width=200, anchor="w")

        for r in rows[:500]:
            self.results.insert("", "end", values=tuple(r))
        
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        if execution_time > 0:
            ttk.Label(self.stats_frame, text=f"⏱️ {execution_time:.3f}s", style="Stats.TLabel").pack(side="left", padx=6)
        if row_count > 0:
            ttk.Label(self.stats_frame, text=f"📊 {row_count} fila(s)", style="Stats.TLabel").pack(side="left", padx=6)
        if len(rows) > 500:
            ttk.Label(self.stats_frame, text=f"⚠️ Mostrando 500 de {len(rows)}", style="Stats.TLabel").pack(side="left", padx=6)


if __name__ == "__main__":
    DBManagerUI().mainloop()
