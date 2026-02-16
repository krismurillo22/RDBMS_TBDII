from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from psycopg2 import Error as PsycopgError

from db.connection import get_connection


@dataclass
class ConnectionInfo:
    name: str = "default"
    host: str = "localhost"
    port: int = 26257
    database: str = "defaultdb"
    user: str = "root"
    password: Optional[str] = None
    sslmode: str = "disable"


class ConnectionService:

    def __init__(self):
        self._current_info: Optional[ConnectionInfo] = None
        self._conn = None  # psycopg2 connection

    def test_connection(self, info: ConnectionInfo) -> Tuple[bool, str]:
        """
        Intenta conectar y ejecutar un SELECT simple.
        Devuelve (ok, mensaje).
        """
        try:
            conn = get_connection(
                host=info.host,
                port=info.port,
                database=info.database,
                user=info.user,
                password=info.password,
                sslmode=info.sslmode,
                default_db=False,
            )
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            conn.close()
            return True, "Conexión exitosa."
        except PsycopgError as e:
            return False, str(e).strip()

    def connect(self, info: ConnectionInfo) -> None:
        self.disconnect()
        self._conn = get_connection(
            host=info.host,
            port=info.port,
            database=info.database,
            user=info.user,
            password=info.password,
            sslmode=info.sslmode,
        )
        self._current_info = info

    def disconnect(self) -> None:
        try:
            if self._conn is not None:
                self._conn.close()
        finally:
            self._conn = None
            self._current_info = None

    def get_conn(self):
        return self._conn

    def get_current_info(self) -> Optional[ConnectionInfo]:
        return self._current_info
