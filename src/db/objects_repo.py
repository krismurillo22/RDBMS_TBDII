from typing import List
from psycopg2.extensions import connection as PGConnection
import re

from db.execute import fetch_all
from db.crdb_system_tables import (LIST_DATABASES, LIST_SCHEMAS, LIST_TABLES_BY_SCHEMA, LIST_VIEWS_BY_SCHEMA,
    LIST_INDEXES_BY_SCHEMA, LIST_FUNCTIONS_BY_SCHEMA, LIST_SEQUENCES_BY_SCHEMA, LIST_TYPES_BY_SCHEMA, GET_TABLE_COLUMNS, GET_COLUMN_DEFAULTS,
    GET_PRIMARY_KEY_COLUMNS, GET_UNIQUE_CONSTRAINTS, GET_TABLE_INDEXES, GET_FOREIGN_KEYS,)
from models.db_object import DbObject

def list_databases(conn: PGConnection) -> list[str]:
    _, rows = fetch_all(conn, LIST_DATABASES)
    return [r[0] for r in rows]

def list_schemas(conn: PGConnection) -> list[str]:
    _, rows = fetch_all(conn, LIST_SCHEMAS)
    return [r[0] for r in rows]

def list_tables_by_schema(conn: PGConnection, schema: str) -> List[DbObject]:
    _, rows = fetch_all(conn, LIST_TABLES_BY_SCHEMA, (schema,))
    return [DbObject(obj_type="table", schema=r[0], name=r[1]) for r in rows]

def list_views_by_schema(conn: PGConnection, schema: str) -> List[DbObject]:
    _, rows = fetch_all(conn, LIST_VIEWS_BY_SCHEMA, (schema,))
    return [DbObject(obj_type="view", schema=r[0], name=r[1]) for r in rows]

def list_indexes_by_schema(conn: PGConnection, schema: str) -> list[tuple[str, str, str]]:
    """
    Retorna: [(schema, table, index), ...]
    """
    _, rows = fetch_all(conn, LIST_INDEXES_BY_SCHEMA, (schema,))
    return rows

def list_functions_by_schema(conn: PGConnection, schema: str) -> list[tuple[str, str]]:
    """
    Retorna: [(schema, function_name), ...]
    """
    _, rows = fetch_all(conn, LIST_FUNCTIONS_BY_SCHEMA, (schema,))
    return rows

def list_sequences_by_schema(conn: PGConnection, schema: str) -> list[tuple[str, str]]:
    """
    Retorna: [(schema, sequence_name), ...]
    """
    _, rows = fetch_all(conn, LIST_SEQUENCES_BY_SCHEMA, (schema,))
    return rows

def list_types_by_schema(conn: PGConnection, schema: str) -> list[tuple[str, str]]:
    """
    Retorna: [(schema, type_name), ...]
    """
    _, rows = fetch_all(conn, LIST_TYPES_BY_SCHEMA, (schema,))
    return rows

def get_table_columns(conn, schema: str, table: str):
    _, rows = fetch_all(conn, GET_TABLE_COLUMNS, (table, schema))
    return rows


def get_primary_key_columns(conn, schema: str, table: str) -> list[str]:
    _, rows = fetch_all(conn, GET_PRIMARY_KEY_COLUMNS, (schema, table))
    return [r[0] for r in rows]


def get_column_defaults(conn, schema: str, table: str) -> dict[str, str]:
    _, rows = fetch_all(conn, GET_COLUMN_DEFAULTS, (schema, table))
    return {r[0]: (r[1] or "") for r in rows}


def get_unique_constraints(conn, schema: str, table: str) -> list[tuple[str, list[str]]]:
    _, rows = fetch_all(conn, GET_UNIQUE_CONSTRAINTS, (schema, table))
    grouped: dict[str, list[str]] = {}
    for cname, col in rows:
        grouped.setdefault(cname, []).append(col)
    return [(cname, cols) for cname, cols in grouped.items()]

def get_table_indexes(conn, schema: str, table: str) -> list[tuple[str, str, str, str]]:
    _, rows = fetch_all(conn, GET_TABLE_INDEXES, (schema, table))

    result = []
    for index_name, is_primary, is_unique, index_def in rows:
        idx_type = "PRIMARY KEY" if is_primary else ("UNIQUE" if is_unique else "BTREE")

        cols = ""
        m = re.search(r"\((.*)\)", index_def)
        if m:
            cols = m.group(1).strip().replace(" ASC", "").replace(" DESC", "")

        unique_str = "" if is_primary else ("UNIQUE" if is_unique else "")
        result.append((index_name, idx_type, cols, unique_str))

    return result

def get_foreign_keys(conn, schema: str, table: str) -> list[tuple[str, str, str, str, str]]:
    _, rows = fetch_all(conn, GET_FOREIGN_KEYS, (schema, table))
    return rows

def list_tables(conn, schema: str = "public"):
    return list_tables_by_schema(conn, schema)

def list_views(conn, schema: str = "public"):
    return list_views_by_schema(conn, schema)
