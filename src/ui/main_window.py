import tkinter as tk
from tkinter import ttk, messagebox

from services.connection_service import ConnectionService, ConnectionInfo
from db.execute import run_sql


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Database Manager Tool")
        self.geometry("1100x650")

        self.conn_service = ConnectionService()

        # Top bar
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        self.lbl_status = ttk.Label(top, text="No conectado")
        self.lbl_status.pack(side="left")

        ttk.Button(top, text="Conectar", command=self.open_login).pack(side="right")

        # Main panels
        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)

        # Left (placeholder: object tree después)
        left = ttk.Frame(body, padding=8)
        body.add(left, weight=1)
        ttk.Label(left, text="Objetos (pendiente)").pack(anchor="w")

        # Right
        right = ttk.Frame(body, padding=8)
        body.add(right, weight=3)

        ttk.Label(right, text="SQL Editor").pack(anchor="w")

        self.txt_sql = tk.Text(right, height=10)
        self.txt_sql.pack(fill="x", expand=False, pady=(4, 6))
        self.txt_sql.insert("1.0", "SELECT now() AS server_time;")

        actions = ttk.Frame(right)
        actions.pack(fill="x")
        ttk.Button(actions, text="Ejecutar", command=self.execute_sql).pack(side="left")

        ttk.Label(right, text="Salida / Resultados").pack(anchor="w", pady=(10, 0))

        self.txt_out = tk.Text(right, height=18)
        self.txt_out.pack(fill="both", expand=True, pady=(4, 0))
        self.txt_out.configure(state="disabled")

        # Al iniciar, pedir login
        self.after(200, self.open_login)

    def set_status_connected(self, info: ConnectionInfo):
        self.lbl_status.configure(
            text=f"Conectado a {info.database} @ {info.host}:{info.port} (user: {info.user})"
        )

    def set_status_disconnected(self):
        self.lbl_status.configure(text="No conectado")

    def open_login(self):
        from ui.dialogs.login_dialog import LoginDialog

        dlg = LoginDialog(self, self.conn_service)
        self.wait_window(dlg)

        info = self.conn_service.get_current_info()
        if info is not None:
            self.set_status_connected(info)
        else:
            self.set_status_disconnected()

    def write_out(self, text: str):
        self.txt_out.configure(state="normal")
        self.txt_out.insert("end", text + "\n")
        self.txt_out.see("end")
        self.txt_out.configure(state="disabled")

    def execute_sql(self):
        conn = self.conn_service.get_conn()
        if conn is None:
            messagebox.showwarning("Sin conexión", "Conéctate primero.")
            return

        sql = self.txt_sql.get("1.0", "end").strip()
        if not sql:
            return

        try:
            result = run_sql(conn, sql)
            if result["type"] == "query":
                self.write_out(result["message"])
                self.write_out(" | ".join(result["columns"]))
                for row in result["rows"][:200]:
                    self.write_out(str(row))
                if len(result["rows"]) > 200:
                    self.write_out(f"... {len(result['rows']) - 200} fila(s) más")
            else:
                self.write_out(result["message"])
        except Exception as e:
            self.write_out(f"ERROR: {e}")
