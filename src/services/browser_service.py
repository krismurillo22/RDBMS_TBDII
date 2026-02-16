from typing import Dict, List
from psycopg2.extensions import connection as PGConnection

from db.objects_repo import list_tables, list_views
from models.db_object import DbObject


def get_browser_data(conn: PGConnection) -> Dict[str, List[DbObject]]:
    """
    Devuelve los objetos para pintar el árbol.
    """
    return {
        "Tables": list_tables(conn),
        "Views": list_views(conn),
    }
