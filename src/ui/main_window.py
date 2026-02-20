import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from services.connection_service import ConnectionService, ConnectionInfo
from services.browser_service import get_browser_data
from ui.widgets.object_tree import ObjectTree
from db.objects_repo import get_table_columns, get_primary_key_columns, get_column_defaults, get_table_indexes, get_foreign_keys
from db.ddl_repo import get_create_table_ddl
from ui.widgets.table_details import TableDetails
from ui.widgets.empty_view import EmptyView
from ui.widgets.ddl_view import DDLView
from ui.widgets.scroll_frame import ScrollFrame
from ui.widgets.sql_runner_view import SqlRunnerView
from ui.widgets.create_table_view import CreateTableView
from ui.widgets.create_view_view import CreateViewView

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Database Manager Tool")
        self.geometry("1100x650")

        self.conn_service = ConnectionService()

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        self.lbl_status = ttk.Label(top, text="No conectado")
        self.lbl_status.pack(side="left")

        ttk.Button(top, text="SQL", command=self.open_sql).pack(side="right", padx=(0, 8))
        ttk.Button(top, text="Conectar", command=self.open_login).pack(side="right")
        ttk.Button(top, text="Crear Tabla", command=self.open_create_table).pack(side="right", padx=(0, 8))
        ttk.Button(top, text="Crear Vista", command=self.open_create_view).pack(side="right", padx=(0, 8))

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body, padding=8)
        body.add(left, weight=1)
        ttk.Label(left, text="Objetos").pack(anchor="w")

        self.obj_tree = ObjectTree(left, self.conn_service, on_select=self.on_object_selected)
        self.obj_tree.pack(fill="both", expand=True)
        self.obj_tree.populate_connections()
        self.obj_tree.auto_expand_active()

        ttk.Button(left, text="Refrescar", command=self.refresh_objects).pack(fill="x", pady=(8, 0))

        right = ttk.Frame(body, padding=8)
        body.add(right, weight=3)
        self.right_container = ttk.Frame(right)
        self.right_container.pack(fill="both", expand=True)
        self.view_empty = EmptyView(self.right_container)
        self.details_scroll = ScrollFrame(self.right_container)
        self.view_details = TableDetails(
            self.details_scroll.inner,
            on_view_ddl=self.handle_view_ddl,
            on_drop=self.handle_drop_table,
            on_edit=self.handle_edit_table,
        )
        self.view_details.pack(fill="both", expand=True)

        self.view_ddl = DDLView(self.right_container, on_back=lambda: self.show_view("details"))

        self.view_sql = SqlRunnerView(
        self.right_container,
            get_conn=self.conn_service.get_conn,
            on_back=self.back_from_sql
        )
        self.view_sql.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.view_create_table = CreateTableView(
            self.right_container,
            get_conn=self.conn_service.get_conn,
            get_databases=self.conn_service.get_databases_active,
            get_schemas_for_db=self.conn_service.get_schemas_for_db,
            get_current_info=self.conn_service.get_current_info,
            switch_database=self.conn_service.switch_database,
            on_back=lambda: self.show_view(self._last_view),
            on_created=self.refresh_objects,)
        self.view_create_table.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.view_create_view = CreateViewView(
            self.right_container,
            get_conn=self.conn_service.get_conn,
            get_databases=self.conn_service.get_databases_active,
            get_schemas_for_db=self.conn_service.get_schemas_for_db,
            get_current_info=self.conn_service.get_current_info,
            switch_database=self.conn_service.switch_database,
            on_back=lambda: self.show_view(self._last_view),
            on_created=self.refresh_objects,)
        self.view_create_view.place(relx=0, rely=0, relwidth=1, relheight=1)


        self._last_view = "empty"


        for v in (self.view_empty, self.details_scroll, self.view_ddl):
            v.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_view("empty")

    def set_status_connected(self, info: ConnectionInfo):
        self.lbl_status.configure(
            text=f"Conectado a {info.database} @ {info.host}:{info.port} (user: {info.user})"
        )

    def show_view(self, name: str):
        if name not in ("sql", "create_table", "create_view"):
            self._last_view = name

        if name == "empty":
            self.view_empty.lift()
        elif name == "details":
            self.details_scroll.lift()
        elif name == "ddl":
            self.view_ddl.lift()
        elif name == "sql":
            self.view_sql.lift()
        elif name == "create_table":
            self.view_create_table.lift()
        elif name == "create_view":
            self.view_create_view.lift()


    def set_status_disconnected(self):
        self.lbl_status.configure(text="No conectado")

    def open_login(self):
        from ui.dialogs.login_dialog import LoginDialog

        dlg = LoginDialog(self, self.conn_service)
        self.wait_window(dlg)
 
        info = self.conn_service.get_current_info()
        if info is not None:
            self.set_status_connected(info)
            self.refresh_objects()
            self.show_view("empty")
        else:
            self.set_status_disconnected()
            self.show_view("empty")

    def refresh_objects(self):
        conn = self.conn_service.get_conn()
        if conn is None:
            return
        self.obj_tree.populate_connections()

    def on_object_selected(self, obj, meta=None):
        conn = self.conn_service.get_conn()
        if conn is None:
            return

        if obj.obj_type != "table":
            from db.ddl_repo import get_object_ddl
            ddl = get_object_ddl(conn, obj, meta or {})
            title = f"{obj.obj_type.upper()} {obj.schema}.{obj.name}"
            self.view_ddl.set_content(title, ddl)
            self.show_view("ddl")
            return

        self.view_details.clear_all()
        self.view_details.current_schema = obj.schema
        self.view_details.current_table = obj.name
        self.view_details.set_header(obj.name, obj.schema)

        # PK columns
        pk_cols = set(get_primary_key_columns(conn, obj.schema, obj.name))
        defaults = get_column_defaults(conn, obj.schema, obj.name)

        # Columnas
        cols = get_table_columns(conn, obj.schema, obj.name)

        columns_rows = []
        for name, dtype, notnull in cols:
            pk_flag = "PK" if name in pk_cols else ""
            default_val = defaults.get(name, "")
            columns_rows.append((name, dtype, "NO" if notnull else "YES", default_val, pk_flag))

        self.view_details.load_columns(columns_rows) 
        idx_rows = get_table_indexes(conn, obj.schema, obj.name)
        self.view_details.load_indexes(idx_rows)
        fk_rows = get_foreign_keys(conn, obj.schema, obj.name)
        self.view_details.load_foreign_keys(fk_rows)

        # Preview
        try:
            from db.execute import fetch_all
            preview_sql = f'SELECT * FROM "{obj.schema}"."{obj.name}" LIMIT 100;'
            pcols, prows = fetch_all(conn, preview_sql)
            self.view_details.load_preview(pcols, prows)
        except Exception:
            self.view_details.load_preview(["info"], [("No se pudo cargar preview.",)])

        self.view_details.current_ddl = get_create_table_ddl(conn, obj.schema, obj.name)
        self.show_view("details")


    def handle_view_ddl(self):
        if not self.view_details.current_table or not self.view_details.current_ddl:
            return
        title = f"Generación de DDL - TABLE {self.view_details.current_table}"
        self.view_ddl.set_content(title, self.view_details.current_ddl)
        self.show_view("ddl")


    def handle_drop_table(self):
        pass

    def handle_edit_table(self):
        pass

    def open_sql(self):
        self.show_view("sql")

    def back_from_sql(self):
        self.show_view(self._last_view)

    def open_create_table(self):
        self.show_view("create_table")

    def open_create_view(self):
        self.show_view("create_view")

    def get_active_info(self) -> Optional[ConnectionInfo]:
        infos, active = self.load_all()
        if not infos:
            return None
        if not active:
            return infos[0]
        for i in infos:
            if i.id == active:
                return i
        return infos[0]




