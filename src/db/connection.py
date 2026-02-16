import psycopg2
from typing import Optional, Dict, Any

DB_HOST = "localhost"
DB_PORT = 26257
DB_NAME = "mi_bd"
DB_USER = "root"
DB_SSLMODE = "disable"


def get_connection(
    host: str = DB_HOST,
    port: int = DB_PORT,
    database: str = DB_NAME,
    user: str = DB_USER,
    password: Optional[str] = None,
    sslmode: str = DB_SSLMODE,
    default_db: bool = False,
    connect_timeout: int = 5,
):
    
    dbname = "defaultdb" if default_db else database

    kwargs: Dict[str, Any] = {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "sslmode": sslmode,
        "connect_timeout": connect_timeout,
        "application_name": "DatabaseManagerTool",
    }

    if password:
        kwargs["password"] = password

    return psycopg2.connect(**kwargs)
