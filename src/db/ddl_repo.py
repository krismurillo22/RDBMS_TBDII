from psycopg2.extensions import connection as PGConnection
from db.objects_repo import get_table_columns, get_primary_key_columns, get_unique_constraints, get_foreign_keys


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

    # Agregar PRIMARY KEY si existe
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
