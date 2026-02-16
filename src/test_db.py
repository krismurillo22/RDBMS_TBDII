from services.connection_service import ConnectionService, ConnectionInfo
from db.execute import run_sql

def main():
    svc = ConnectionService()

    info = ConnectionInfo(
        name="local",
        host="localhost",
        port=26257,
        database="defaultdb",
        user="root",
        password=None,
        sslmode="disable",
    )

    ok, msg = svc.test_connection(info)
    print(ok, msg)

    if ok:
        svc.connect(info)
        conn = svc.get_conn()

        r = run_sql(conn, "SELECT now() AS server_time;")
        print(r["columns"], r["rows"][:1])

        svc.disconnect()

if __name__ == "__main__":
    main()
