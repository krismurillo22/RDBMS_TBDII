from typing import Any, Iterable, Optional, Tuple, List, Dict
from psycopg2.extensions import connection as PGConnection
from psycopg2 import Error as PsycopgError


def is_select(sql: str) -> bool:
    s = (sql or "").strip().lower()
    return s.startswith("select") or s.startswith("with")


def fetch_all(
    conn: PGConnection,
    sql: str,
    params: Optional[Iterable[Any]] = None,
) -> Tuple[List[str], List[tuple]]:

    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        columns = [d[0] for d in (cur.description or [])]
        return columns, rows


def execute(
    conn: PGConnection,
    sql: str,
    params: Optional[Iterable[Any]] = None,
) -> int:
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            affected = cur.rowcount
        conn.commit()
        return affected
    except PsycopgError:
        conn.rollback()
        raise


def run_sql(
    conn: PGConnection,
    sql: str,
    params: Optional[Iterable[Any]] = None,
) -> Dict[str, Any]:
    
    sql = (sql or "").strip()
    if not sql:
        return {"type": "command", "message": "SQL vacío."}

    if is_select(sql):
        cols, rows = fetch_all(conn, sql, params)
        return {
            "type": "query",
            "columns": cols,
            "rows": rows,
            "message": f"{len(rows)} fila(s).",
        }

    affected = execute(conn, sql, params)
    return {
        "type": "command",
        "affected": affected,
        "message": f"OK. Filas afectadas: {affected}.",
    }
