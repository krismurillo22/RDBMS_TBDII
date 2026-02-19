import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple
from psycopg2 import Error as PsycopgError
from db.connection import get_connection
from db.objects_repo import list_databases, list_schemas

@dataclass
class ConnectionInfo:
    id: str
    name: str
    host: str
    port: int
    database: str
    user: str
    password: Optional[str] = None
    sslmode: str = "disable"


class ConnectionService:
    def __init__(self, json_path: str = "connections.json"):
            p = Path(json_path)

            if not p.exists():
                alt = Path(__file__).resolve().parents[2] / json_path
                if alt.exists():
                    p = alt

            self.json_path = p
            self._current_info = None
            self._conn = None

    def load_all(self) -> tuple[list[ConnectionInfo], Optional[str]]:
        data = json.loads(self.json_path.read_text(encoding="utf-8"))
        active = data.get("active")
        infos = []
        for c in data.get("connections", []):
            infos.append(ConnectionInfo(
                id=c["id"],
                name=c["name"],
                host=c["host"],
                port=int(c["port"]),
                database=c.get("database", "defaultdb"),
                user=c["user"],
                password=c.get("password"),
                sslmode=c.get("sslmode", "disable"),
            ))
        return infos, active

    def test_connection(self, info: ConnectionInfo) -> Tuple[bool, str]:
        try:
            conn = get_connection(
                host=info.host, port=info.port, database=info.database,
                user=info.user, password=info.password, sslmode=info.sslmode
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
            host=info.host, port=info.port, database=info.database,
            user=info.user, password=info.password, sslmode=info.sslmode
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

    def open_temp_conn(self, info: ConnectionInfo, database: str):
        return get_connection(
            host=info.host, port=info.port, database=database,
            user=info.user, password=info.password, sslmode=info.sslmode
        )

    def get_databases(self, info: ConnectionInfo) -> list[str]:
        conn = self.open_temp_conn(info, info.database)
        try:
            return list_databases(conn)
        finally:
            conn.close()

    def get_schemas(self, info: ConnectionInfo, database: str) -> list[str]:
        conn = self.open_temp_conn(info, database)
        try:
            return list_schemas(conn)
        finally:
            conn.close()
