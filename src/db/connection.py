import psycopg2

# Datos de conexión directos
DB_HOST = "localhost"
DB_PORT = 26257
DB_NAME = "mi_bd"
DB_USER = "root"
DB_SSLMODE = "disable"

def get_connection(default_db=False):
    db = "defaultdb" if default_db else DB_NAME
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=db,
        user=DB_USER,
        sslmode=DB_SSLMODE
    )
