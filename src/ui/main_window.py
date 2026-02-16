import tkinter as tk
from tkinter import ttk, messagebox

from services.connection_service import ConnectionService, ConnectionInfo
from services.browser_service import get_browser_data
from ui.widgets.object_tree import ObjectTree
from db.objects_repo import get_table_columns
from db.ddl_repo import get_create_table_ddl
from ui.widgets.table_details import TableDetails
from ui.widgets.empty_view import EmptyView
from ui.widgets.ddl_view import DDLView
from ui.widgets.scroll_frame import ScrollFrame



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

        ttk.Button(top, text="Conectar", command=self.open_login).pack(side="right")

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body, padding=8)
        body.add(left, weight=1)
        ttk.Label(left, text="Objetos").pack(anchor="w")

        self.obj_tree = ObjectTree(left, on_select=self.on_object_selected)
        self.obj_tree.pack(fill="both", expand=True, pady=(6, 0))

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

        for v in (self.view_empty, self.details_scroll, self.view_ddl):
            v.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_view("empty")
        self.after(200, self.open_login)

    def set_status_connected(self, info: ConnectionInfo):
        self.lbl_status.configure(
            text=f"Conectado a {info.database} @ {info.host}:{info.port} (user: {info.user})"
        )

    def show_view(self, name: str):
        if name == "empty":
            self.view_empty.lift()
        elif name == "details":
            self.details_scroll.lift()
        elif name == "ddl":
            self.view_ddl.lift()


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
        data = get_browser_data(conn)
        self.obj_tree.populate(data)

    def on_object_selected(self, obj):
        conn = self.conn_service.get_conn()
        if conn is None:
            return

        if obj.obj_type != "table":
            return

        self.view_details.clear_all()
        self.view_details.current_schema = obj.schema
        self.view_details.current_table = obj.name
        self.view_details.set_header(obj.name, obj.schema)

        cols = get_table_columns(conn, obj.schema, obj.name)
        columns_rows = []
        for name, dtype, notnull in cols:
            columns_rows.append((name, dtype, "NO" if notnull else "YES", "", "")) 
        self.view_details.load_columns(columns_rows)

        # 2) Preview
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



