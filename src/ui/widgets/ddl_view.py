import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class DDLView(ttk.Frame):
    def __init__(self, parent, on_back=None):
        super().__init__(parent)
        self.on_back = on_back
        self.current_title = ""
        self.current_ddl = ""

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        ttk.Button(top, text="← Volver", command=self._back).pack(side="left", padx=(0, 8))
        self.lbl = ttk.Label(top, text="Generación de DDL", style="Title.TLabel")
        self.lbl.pack(side="left")

        btns = ttk.Frame(top)
        btns.pack(side="right")
        ttk.Button(btns, text="Copiar", command=self._copy).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Descargar", command=self._save).pack(side="left")

        body = ttk.Frame(self, padding=8)
        body.pack(fill="both", expand=True)

        self.txt = tk.Text(body, wrap="none")
        self.txt.pack(fill="both", expand=True)
        self.txt.configure(bg="#0b1220", fg="#e5e7eb", insertbackground="#e5e7eb", relief="flat")



    def set_content(self, title: str, ddl: str):
        self.current_title = title
        self.current_ddl = ddl
        self.lbl.configure(text=title)

        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", ddl)

    def _back(self):
        if self.on_back:
            self.on_back()

    def _copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.current_ddl)
        messagebox.showinfo("Copiado", "DDL copiado al portapapeles.")

    def _save(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL", "*.sql"), ("Text", "*.txt"), ("All", "*.*")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.current_ddl)
        messagebox.showinfo("Guardado", "Archivo guardado correctamente.")
