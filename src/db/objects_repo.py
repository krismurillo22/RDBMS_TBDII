from typing import List
from psycopg2.extensions import connection as PGConnection

from db.execute import fetch_all
from db.crdb_system_tables import LIST_TABLES, LIST_VIEWS, GET_TABLE_COLUMNS
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