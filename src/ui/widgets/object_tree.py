import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from models.db_object import DbObject


class ObjectTree(ttk.Frame):
    def __init__(self, parent, on_select: Optional[Callable[[DbObject], None]] = None):
        super().__init__(parent)
        self.on_select = on_select

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill="both", expand=True)

        self._node_to_obj = {}  # item_id -> DbObject

        self.tree.bind("<<TreeviewSelect>>", self._handle_select)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._node_to_obj.clear()

    def populate(self, data: dict):
        """
        data: { "Tables": [DbObject...], "Views": [DbObject...] }
        """
        self.clear()

        for group_name, objs in data.items():
            group_id = self.tree.insert("", "end", text=group_name, open=True)
            schemas = {}
            for o in objs:
                schemas.setdefault(o.schema, []).append(o)

            for schema_name, schema_objs in schemas.items():
                schema_id = self.tree.insert(group_id, "end", text=schema_name, open=False)
                for o in schema_objs:
                    item_id = self.tree.insert(schema_id, "end", text=o.name)
                    self._node_to_obj[item_id] = o

    def _handle_select(self, _evt):
        sel = self.tree.selection()
        if not sel:
            return
        item_id = sel[0]
        obj = self._node_to_obj.get(item_id)
        if obj and self.on_select:
            self.on_select(obj)
