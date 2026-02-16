from db.connection import get_connection
from db.execute import run_sql

def main():
    conn = get_connection(default_db=True)

    # Query
    r1 = run_sql(conn, "SELECT now() AS server_time;")
    print(r1["type"], r1["columns"], r1["rows"][:1], r1["message"])

    # Command (crea una tabla de prueba)
    run_sql(conn, "CREATE TABLE IF NOT EXISTS public.demo (id INT PRIMARY KEY, name STRING);")
    r2 = run_sql(conn, "INSERT INTO public.demo (id, name) VALUES (1, 'hola') ON CONFLICT (id) DO NOTHING;")
    print(r2["type"], r2["message"])

    # Query
    r3 = run_sql(conn, "SELECT * FROM public.demo;")
    print(r3["columns"], r3["rows"])

    conn.close()

if __name__ == "__main__":
    main()
