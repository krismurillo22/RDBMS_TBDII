from db.connection import get_connection

def init_db():
    # Conexión a defaultdb para crear la base si no existe
    conn = get_connection(default_db=True)  
    cur = conn.cursor()

    # Crear la base de datos si no existe
    cur.execute("CREATE DATABASE IF NOT EXISTS mi_bd")
    conn.commit()
    cur.close()
    conn.close()

    # Conectar a la base recién creada
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre STRING NOT NULL,
            email STRING
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
