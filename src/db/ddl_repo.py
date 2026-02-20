from psycopg2.extensions import connection as PGConnection
from db.objects_repo import get_table_columns, get_primary_key_columns, get_unique_constraints, get_foreign_keys
from db.execute import fetch_all

def get_create_table_ddl(conn: PGConnection, schema: str, table: str) -> str:
    columns = get_table_columns(conn, schema, table)
    pk_cols = get_primary_key_columns(conn, schema, table)
    uniques = get_unique_constraints(conn, schema, table)

    if not columns:
        return f"-- No se encontraron columnas para {schema}.{table}"

    lines = []
    for name, dtype, notnull in columns:
        line = f'    "{name}" {dtype}'
        if notnull:
            line += " NOT NULL"
        lines.append(line)

    if pk_cols:
        pk_list = ", ".join([f'"{c}"' for c in pk_cols])
        lines.append(f"    PRIMARY KEY ({pk_list})")

    for cname, ucols in uniques:
        col_list = ", ".join([f'"{c}"' for c in ucols])
        lines.append(f'    CONSTRAINT "{cname}" UNIQUE ({col_list})')

    fks = get_foreign_keys(conn, schema, table)

    for fk_name, col, ref_schema, ref_table, ref_col in fks:
        lines.append(
            f'    CONSTRAINT "{fk_name}" FOREIGN KEY ("{col}") '
            f'REFERENCES "{ref_schema}"."{ref_table}" ("{ref_col}")'
        )

    columns_sql = ",\n".join(lines)

    ddl = f"""CREATE TABLE "{schema}"."{table}" (
{columns_sql}
);"""
    return ddl

def _scalar(conn, sql: str, params=None) -> str:
    cols, rows = fetch_all(conn, sql, params)
    if not rows:
        return ""
    if len(rows[0]) == 1:
        return rows[0][0] or ""
    return rows[0][-1] or ""

def get_object_ddl(conn, obj, meta: dict) -> str:
    schema = obj.schema
    name = obj.name

    try:
        if obj.obj_type == "view":
            return _scalar(conn, f'SHOW CREATE VIEW "{schema}"."{name}";')

        if obj.obj_type == "sequence":
            return _scalar(conn, f'SHOW CREATE SEQUENCE "{schema}"."{name}";')

        if obj.obj_type == "table":
            return _scalar(conn, f'SHOW CREATE TABLE "{schema}"."{name}";')

        if obj.obj_type == "index":
            tbl = meta.get("table")
            if not tbl:
                return "-- No se encontró la tabla del índice (meta.table)."

            create_tbl = _scalar(conn, f'SHOW CREATE TABLE "{schema}"."{tbl}";')
            if not create_tbl:
                return "-- No se pudo obtener SHOW CREATE TABLE."

            lines = [ln for ln in create_tbl.splitlines() if name in ln]
            if lines:
                return "\n".join(lines)
            return create_tbl 

        if obj.obj_type == "function":
            try:
                return _scalar(conn, f'SHOW CREATE FUNCTION "{schema}"."{name}";')
            except Exception:
                return "-- CockroachDB no está soportado en esta versión"

        if obj.obj_type == "type":
            sql = """
            SELECT
              'TYPE ' || n.nspname || '.' || t.typname || E'\\n' ||
              'oid: ' || t.oid::STRING || E'\\n' ||
              'category: ' || t.typcategory || E'\\n' ||
              'is_defined: ' || (NOT t.typisdefined)::STRING
            FROM pg_catalog.pg_type t
            INNER JOIN pg_catalog.pg_namespace n
              ON n.oid = t.typnamespace
            WHERE n.nspname = %s
              AND t.typname = %s
            LIMIT 1;
            """
            out = _scalar(conn, sql, (schema, name))
            return out or "-- Type no encontrado o no soportado."

        return f"-- Tipo no soportado: {obj.obj_type}"

    except Exception as e:
        return f"-- Error obteniendo DDL: {e}"