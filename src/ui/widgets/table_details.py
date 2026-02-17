import tkinter as tk
from tkinter import ttk


class TableDetails(ttk.Frame):
    """
    Panel derecho tipo 'ficha' de tabla:
    - Header con nombre + botones
    - Sección Columnas (Treeview)
    - Sección Índices (Treeview)
    - Sección Preview (Treeview)
    """

    def __init__(self, parent, on_view_ddl=None, on_drop=None, on_edit=None):
        super().__init__(parent)
        self.on_view_ddl = on_view_ddl
        self.on_drop = on_drop
        self.on_edit = on_edit

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 8))

        left = ttk.Frame(header)
        left.pack(side="left", fill="x", expand=True)

        self.lbl_title = ttk.Label(left, text="(selecciona una tabla)", style="Title.TLabel")
        self.lbl_title.pack(anchor="w")

        self.lbl_sub = ttk.Label(left, text="", style="Sub.TLabel")
        self.lbl_sub.pack(anchor="w")

        right = ttk.Frame(header)
        right.pack(side="right")

        self.btn_ddl = ttk.Button(right, text="Ver DDL", command=lambda: self.on_view_ddl() if self.on_view_ddl else None)
        self.btn_ddl.pack(side="left", padx=(0, 8))

        self.btn_edit = ttk.Button(right, text="Modificar", command=lambda: self.on_edit() if self.on_edit else None)
        self.btn_edit.pack(side="left", padx=(0, 8))

        self.btn_drop = ttk.Button(right, text="Eliminar", command=lambda: self.on_drop() if self.on_drop else None)
        self.btn_drop.pack(side="left")


        self._section_label("Columnas").pack(anchor="w")
        self.columns_tree = self._make_tree(
            columns=("name", "type", "nullable", "default", "pk"),
            headings=("Nombre", "Tipo", "Nullable", "Default", "PK"),
            widths=(160, 180, 90, 220, 60),
        )
        self.columns_tree.pack(fill="x", pady=(6, 14))

        self._section_label("Índices").pack(anchor="w")
        self.indexes_tree = self._make_tree(
            columns=("name", "type", "cols", "unique"),
            headings=("Nombre", "Tipo", "Columnas", "Único"),
            widths=(220, 120, 220, 80),
        )
        self.indexes_tree.pack(fill="x", pady=(6, 14))

        self._section_label("Foreign Keys").pack(anchor="w")
        self.fk_tree = self._make_tree(
            columns=("name", "col", "ref"),
            headings=("Nombre", "Columna", "Referencia"),
            widths=(220, 180, 360),
        )
        self.fk_tree.pack(fill="x", pady=(6, 14))

        self._section_label("Vista previa de datos (primeras 100 filas)").pack(anchor="w")
        self.preview_tree = ttk.Treeview(self, show="headings")
        self.preview_tree.pack(fill="both", expand=True, pady=(6, 0))

        self.current_schema = None
        self.current_table = None
        self.current_ddl = None

    def _section_label(self, text: str) -> ttk.Label:
        return ttk.Label(self, text=text, style="Section.TLabel")

    def _make_tree(self, columns, headings, widths):
        tree = ttk.Treeview(self, columns=columns, show="headings", height=6)
        tree.configure(style="Treeview")
        for col, head, w in zip(columns, headings, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, anchor="w", stretch=True)
        return tree

    def set_header(self, table_name: str, schema_name: str):
        self.lbl_title.configure(text=table_name)
        self.lbl_sub.configure(text=f"Table · {schema_name}")

    def clear_all(self):
        for t in (self.columns_tree, self.indexes_tree):
            for i in t.get_children():
                t.delete(i)

        # preview
        for i in self.preview_tree.get_children():
            self.preview_tree.delete(i)
        self.preview_tree["columns"] = ()

        self.current_schema = None
        self.current_table = None
        self.current_ddl = None

    def load_columns(self, rows):
        for i in self.columns_tree.get_children():
            self.columns_tree.delete(i)
        for i, r in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.columns_tree.insert("", "end", values=r, tags=(tag,))
            
        self.columns_tree.tag_configure("even", background="#0b1220")
        self.columns_tree.tag_configure("odd", background="#132038")


    def load_indexes(self, rows):
        for i in self.indexes_tree.get_children():
            self.indexes_tree.delete(i)
        for r in rows:
            self.indexes_tree.insert("", "end", values=r)

    def load_preview(self, columns, rows):
        self.preview_tree.delete(*self.preview_tree.get_children())
        self.preview_tree["columns"] = columns
        for c in columns:
            self.preview_tree.heading(c, text=c)
            self.preview_tree.column(c, width=140, anchor="w", stretch=True)

        for r in rows:
            self.preview_tree.insert("", "end", values=r)

    def load_foreign_keys(self, rows):
        for i in self.fk_tree.get_children():
            self.fk_tree.delete(i)

        for r in rows:
            fk_name, col, ref_schema, ref_table, ref_col = r
            ref = f'{ref_schema}.{ref_table}({ref_col})'
            self.fk_tree.insert("", "end", values=(fk_name, col, ref))

