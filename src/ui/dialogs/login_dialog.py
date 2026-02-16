import tkinter as tk
from tkinter import ttk, messagebox

from services.connection_service import ConnectionService, ConnectionInfo


class LoginDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, conn_service: ConnectionService):
        super().__init__(parent)
        self.title("Conectar a base de datos")
        self.resizable(False, False)
        self.conn_service = conn_service

        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        # Campos
        self.var_host = tk.StringVar(value="localhost")
        self.var_port = tk.StringVar(value="26257")
        self.var_db = tk.StringVar(value="defaultdb")
        self.var_user = tk.StringVar(value="root")
        self.var_pass = tk.StringVar(value="")
        self.var_ssl = tk.StringVar(value="disable")

        self._row(frm, "Host", self.var_host, 0)
        self._row(frm, "Port", self.var_port, 1)
        self._row(frm, "Database", self.var_db, 2)
        self._row(frm, "User", self.var_user, 3)
        self._row(frm, "Password", self.var_pass, 4, show="*")

        ttk.Label(frm, text="SSL Mode").grid(row=5, column=0, sticky="w", pady=4)
        cmb = ttk.Combobox(frm, textvariable=self.var_ssl, values=["disable", "require"], width=27, state="readonly")
        cmb.grid(row=5, column=1, sticky="w", pady=4)

        # Botones
        btns = ttk.Frame(frm)
        btns.grid(row=6, column=0, columnspan=2, sticky="e", pady=(12, 0))

        ttk.Button(btns, text="Probar", command=self.on_test).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Conectar", command=self.on_connect).pack(side="left")

        self.bind("<Return>", lambda e: self.on_connect())
        self.bind("<Escape>", lambda e: self.destroy())

        self._center(parent)

    def _row(self, parent, label, var, r, show=None):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", pady=4)
        ent = ttk.Entry(parent, textvariable=var, width=30, show=show)
        ent.grid(row=r, column=1, sticky="w", pady=4)

    def _center(self, parent: tk.Tk):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _get_info(self) -> ConnectionInfo:
        return ConnectionInfo(
            name="temp",
            host=self.var_host.get().strip(),
            port=int(self.var_port.get().strip()),
            database=self.var_db.get().strip(),
            user=self.var_user.get().strip(),
            password=self.var_pass.get().strip() or None,
            sslmode=self.var_ssl.get().strip() or "disable",
        )

    def on_test(self):
        try:
            info = self._get_info()
            ok, msg = self.conn_service.test_connection(info)
            if ok:
                messagebox.showinfo("OK", msg)
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_connect(self):
        try:
            info = self._get_info()
            ok, msg = self.conn_service.test_connection(info)
            if not ok:
                messagebox.showerror("Error", msg)
                return

            self.conn_service.connect(info)
            messagebox.showinfo("Conectado", "Conectado correctamente.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
