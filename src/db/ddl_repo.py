from psycopg2.extensions import connection as PGConnection
from db.objects_repo import get_table_columns


def get_create_table_ddl(conn: PGConnection, schema: str, table: str) -> str:
    """
    Reconstruye el CREATE TABLE usando metadata.
    """
    columns = get_table_columns(conn, schema, table)

    if not columns:
        return f"-- No se encontraron columnas para {schema}.{table}"

    lines = []

    for col in columns:
        name, dtype, notnull = col
        line = f"    {name} {dtype}"
        if notnull:
            line += " NOT NULL"
        lines.append(line)

    columns_sql = ",\n".join(lines)

    ddl = f"""CREATE TABLE {schema}.{table} (
{columns_sql}
);"""

    return ddl
