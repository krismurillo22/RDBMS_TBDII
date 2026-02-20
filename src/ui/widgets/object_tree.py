import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Any

from models.db_object import DbObject
from services.connection_service import ConnectionInfo
from db.objects_repo import (
    list_tables_by_schema,
    list_views_by_schema,
    list_indexes_by_schema,
    list_functions_by_schema,
    list_sequences_by_schema,
    list_types_by_schema,
)

DUMMY = "__DUMMY__"

class ObjectTree(ttk.Frame):
    def __init__(self, parent, connection_service, on_select: Optional[Callable[[DbObject], None]] = None):
        super().__init__(parent)
        self.on_select = on_select
        self.conn_service = connection_service

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill="both", expand=True)

        self._node_meta: dict[str, dict[str, Any]] = {} 
        self._node_to_obj: dict[str, DbObject] = {}      

        self.tree.bind("<<TreeviewSelect>>", self._handle_select)
        self.tree.bind("<<TreeviewOpen>>", self._handle_open)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._node_meta.clear()
        self._node_to_obj.clear()

    def populate_connections(self):
        self.clear()
        infos, active = self.conn_service.load_all()

        for info in infos:
            text = f"{info.name} ({info.host}:{info.port})"
            conn_id = self.tree.insert("", "end", text=text, open=False)
            self._node_meta[conn_id] = {"kind": "connection", "info": info}
            self._add_dummy(conn_id)

            if active and info.id == active:
                self.tree.item(conn_id, open=True)

    def _add_dummy(self, parent_id: str):
        dummy = self.tree.insert(parent_id, "end", text="Cargando...")
        self._node_meta[dummy] = {"kind": DUMMY}

    def _has_dummy(self, node_id: str) -> bool:
        children = self.tree.get_children(node_id)
        return len(children) == 1 and self._node_meta.get(children[0], {}).get("kind") == DUMMY

    def _clear_children(self, node_id: str):
        for ch in self.tree.get_children(node_id):
            self.tree.delete(ch)
            self._node_meta.pop(ch, None)
            self._node_to_obj.pop(ch, None)

    def _handle_open(self, _evt):
        node_id = self.tree.focus()
        meta = self._node_meta.get(node_id)
        if not meta:
            return

        if not self._has_dummy(node_id):
            return

        self._clear_children(node_id)

        kind = meta["kind"]

        if kind == "connection":
            self._load_databases(node_id, meta["info"])

        elif kind == "database":
            self._load_schemas(node_id, meta["info"], meta["database"])

        elif kind == "schema":
            self._load_schema_folders(node_id, meta["info"], meta["database"], meta["schema"])

        elif kind == "folder_tables":
            self._load_tables(node_id, meta["info"], meta["database"], meta["schema"])

        elif kind == "folder_views":
            self._load_views(node_id, meta["info"], meta["database"], meta["schema"])

        elif kind == "folder_indexes":
            self._load_indexes(node_id, meta["info"], meta["database"], meta["schema"])

        elif kind == "folder_functions":
            self._load_functions(node_id, meta["info"], meta["database"], meta["schema"])

        elif kind == "folder_sequences":
            self._load_sequences(node_id, meta["info"], meta["database"], meta["schema"])

        elif kind == "folder_types":
            self._load_types(node_id, meta["info"], meta["database"], meta["schema"])

    def _load_databases(self, conn_node: str, info):
        dbs = self.conn_service.get_databases(info)
        for db in dbs:
            db_id = self.tree.insert(conn_node, "end", text=db, open=False)
            self._node_meta[db_id] = {"kind": "database", "info": info, "database": db}
            self._add_dummy(db_id)

    def _load_schemas(self, db_node: str, info, database: str):
        schemas = self.conn_service.get_schemas(info, database)
        for sch in schemas:
            sch_id = self.tree.insert(db_node, "end", text=sch, open=False)
            self._node_meta[sch_id] = {"kind": "schema", "info": info, "database": database, "schema": sch}
            self._add_dummy(sch_id)

    def _load_schema_folders(self, schema_node: str, info, database: str, schema: str):
        folders = [
            ("Tables", "folder_tables"),
            ("Views", "folder_views"),
            ("Indexes", "folder_indexes"),
            ("Functions", "folder_functions"),
            ("Sequences", "folder_sequences"),
            ("Types", "folder_types"),
        ]
        for label, fkind in folders:
            fid = self.tree.insert(schema_node, "end", text=label, open=False)
            self._node_meta[fid] = {"kind": fkind, "info": info, "database": database, "schema": schema}
            self._add_dummy(fid)

    def _open_meta_conn(self, info, database: str):
        return self.conn_service.open_temp_conn(info, database)

    def _load_tables(self, folder_node: str, info, database: str, schema: str):
        conn = self._open_meta_conn(info, database)
        try:
            tables = list_tables_by_schema(conn, schema)
        finally:
            conn.close()

        for t in tables:
            tid = self.tree.insert(folder_node, "end", text=t.name, open=False)
            self._node_to_obj[tid] = t
            self._node_meta[tid] = {"kind": "table", "info": info, "database": database, "schema": schema, "name": t.name}

    def _load_views(self, folder_node: str, info, database: str, schema: str):
        conn = self._open_meta_conn(info, database)
        try:
            views = list_views_by_schema(conn, schema)
        finally:
            conn.close()

        for v in views:
            vid = self.tree.insert(folder_node, "end", text=v.name, open=False)
            self._node_to_obj[vid] = v
            self._node_meta[vid] = {"kind": "view", "info": info, "database": database, "schema": schema, "name": v.name}

    def _load_indexes(self, folder_node: str, info, database: str, schema: str):
        conn = self._open_meta_conn(info, database)
        try:
            rows = list_indexes_by_schema(conn, schema)
        finally:
            conn.close()

        by_table = {}
        for sch, tbl, idx in rows:
            by_table.setdefault(tbl, []).append(idx)

        for tbl, idxs in by_table.items():
            tbl_id = self.tree.insert(folder_node, "end", text=tbl, open=False)
            self._node_meta[tbl_id] = {"kind": "idx_table", "info": info, "database": database, "schema": schema, "table": tbl}
            for idx in idxs:
                iid = self.tree.insert(tbl_id, "end", text=idx, open=False)

                dbo = DbObject(obj_type="index", schema=schema, name=idx)
                self._node_to_obj[iid] = dbo
                self._node_meta[iid] = {
                    "kind": "index",
                    "info": info,
                    "database": database,
                    "schema": schema,
                    "table": tbl,
                    "index": idx,
                }
    def _load_functions(self, folder_node: str, info, database: str, schema: str):
        conn = self._open_meta_conn(info, database)
        try:
            rows = list_functions_by_schema(conn, schema)
        finally:
            conn.close()

        for sch, fname in rows:
            fid = self.tree.insert(folder_node, "end", text=fname, open=False)
            dbo = DbObject(obj_type="function", schema=schema, name=fname)
            self._node_to_obj[fid] = dbo
            self._node_meta[fid] = {"kind": "function", "info": info, "database": database, "schema": schema, "name": fname}

    def _load_sequences(self, folder_node: str, info, database: str, schema: str):
        conn = self._open_meta_conn(info, database)
        try:
            rows = list_sequences_by_schema(conn, schema)
        finally:
            conn.close()

        for sch, sname in rows:
            sid = self.tree.insert(folder_node, "end", text=sname, open=False)
            dbo = DbObject(obj_type="sequence", schema=schema, name=sname)
            self._node_to_obj[sid] = dbo
            self._node_meta[sid] = {"kind": "sequence", "info": info, "database": database, "schema": schema, "name": sname}

    def _load_types(self, folder_node: str, info, database: str, schema: str):
        conn = self._open_meta_conn(info, database)
        try:
            rows = list_types_by_schema(conn, schema)
        finally:
            conn.close()

        for sch, tname in rows:
            tid = self.tree.insert(folder_node, "end", text=tname, open=False)
            dbo = DbObject(obj_type="type", schema=schema, name=tname)
            self._node_to_obj[tid] = dbo
            self._node_meta[tid] = {"kind": "type", "info": info, "database": database, "schema": schema, "name": tname}

    def _handle_select(self, _evt):
        sel = self.tree.selection()
        if not sel:
            return

        item_id = sel[0]
        obj = self._node_to_obj.get(item_id)
        meta = self._node_meta.get(item_id, {})

        if obj is None:
            return

        if obj.obj_type == "table":
            info = meta.get("info")
            database = meta.get("database")
            if info and database:
                cur = self.conn_service.get_current_info()
                if cur is None or cur.database != database:
                    from services.connection_service import ConnectionInfo
                    self.conn_service.connect(ConnectionInfo(
                        id=info.id, name=info.name, host=info.host, port=info.port,
                        database=database, user=info.user, password=info.password, sslmode=info.sslmode,))

        if self.on_select:
            self.on_select(obj, meta)

    def auto_expand_active(self):
        infos, active = self.conn_service.load_all()
        if not active:
            return
        for item in self.tree.get_children(""):
            meta = self._node_meta.get(item, {})
            info = meta.get("info")
            if meta.get("kind") == "connection" and info and info.id == active:
                self.tree.item(item, open=True)
                self.tree.focus(item)
                self.tree.selection_set(item)
                self._handle_open(None)
                break
