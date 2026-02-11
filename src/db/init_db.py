from db.connection import get_connection

def init_db():
    conn = get_connection(default_db=True)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS mi_bd")
    cur.close()
    conn.close()

    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT PRIMARY KEY DEFAULT unique_rowid(),
            nombre STRING NOT NULL,
            email STRING
        )
    """)

    cur.close()
    conn.close()
