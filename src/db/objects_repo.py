from typing import List
from psycopg2.extensions import connection as PGConnection
import re

from db.execute import fetch_all
from db.crdb_system_tables import LIST_TABLES, LIST_VIEWS, GET_TABLE_COLUMNS, GET_COLUMN_DEFAULTS, GET_PRIMARY_KEY_COLUMNS, GET_UNIQUE_CONSTRAINTS, GET_TABLE_INDEXES
from db.crdb_system_tables import GET_FOREIGN_KEYS
from models.db_object import DbObject


def list_tables(conn: PGConnection) -> List[DbObject]:
    cols, rows = fetch_all(conn, LIST_TABLES)
    return [DbObject(obj_type="table", schema=r[0], name=r[1]) for r in rows]


def list_views(conn: PGConnection) -> List[DbObject]:
    cols, rows = fetch_all(conn, LIST_VIEWS)
    return [DbObject(obj_type="view", schema=r[0], name=r[1]) for r in rows]

def get_table_columns(conn, schema: str, table: str):
    cols, rows = fetch_all(conn, GET_TABLE_COLUMNS, (table, schema))
    return rows

def get_primary_key_columns(conn, schema: str, table: str) -> list[str]:
    cols, rows = fetch_all(conn, GET_PRIMARY_KEY_COLUMNS, (schema, table))
    return [r[0] for r in rows]

def get_column_defaults(conn, schema: str, table: str) -> dict[str, str]:
    cols, rows = fetch_all(conn, GET_COLUMN_DEFAULTS, (schema, table))
    return {r[0]: (r[1] or "") for r in rows}

def get_unique_constraints(conn, schema: str, table: str) -> list[tuple[str, list[str]]]:
    """
    Retorna: [(constraint_name, [col1, col2, ...]), ...]
    """
    _, rows = fetch_all(conn, GET_UNIQUE_CONSTRAINTS, (schema, table))

    grouped: dict[str, list[str]] = {}
    for cname, col in rows:
        grouped.setdefault(cname, []).append(col)

    return [(cname, cols) for cname, cols in grouped.items()]

def get_table_indexes(conn, schema: str, table: str) -> list[tuple[str, str, str, str]]:
    """
    Retorna filas para tu grid de Índices:
    (Nombre, Tipo, Columnas, Único)
    """
    _, rows = fetch_all(conn, GET_TABLE_INDEXES, (schema, table))

    result = []
    for index_name, is_primary, is_unique, index_def in rows:
        # Tipo: PRIMARY KEY / UNIQUE / BTREE (si se puede inferir)
        idx_type = "PRIMARY KEY" if is_primary else ("UNIQUE" if is_unique else "BTREE")

        # Sacar columnas de la definición: ... ON schema.table USING ... (col1, col2)
        cols = ""
        m = re.search(r"\((.*)\)", index_def)
        if m:
            cols = m.group(1).strip()
            cols = cols.replace(" ASC", "").replace(" DESC", "")


        if is_primary:
            unique_str = ""
        elif is_unique:
            unique_str = "UNIQUE"
        else:
            unique_str = ""

        result.append((index_name, idx_type, cols, unique_str))
    return result

def get_foreign_keys(conn, schema: str, table: str) -> list[tuple[str, str, str, str, str]]:
    """
    Retorna lista de FKs:
    (fk_name, column_name, ref_schema, ref_table, ref_column)
    """
    _, rows = fetch_all(conn, GET_FOREIGN_KEYS, (schema, table))
    return rows

def list_databases(conn) -> list[str]:
    cols, rows = fetch_all(conn, "SHOW DATABASES;")
    return [r[0] for r in rows]