import getpass
import os

import psycopg

host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "5433"))
dbname = os.getenv("DB_NAME", "nepal_data")
user = os.getenv("DB_USER", "pipeline_user")

password = os.getenv("DB_PASSWORD")
if not password:
    password = getpass.getpass(
        f"Enter PostgreSQL password for {user}: "
    )

try:
    with psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        connect_timeout=5,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    current_database(),
                    current_user,
                    inet_server_port(),
                    version();
            """)
            database, current_user, server_port, version = cur.fetchone()

            print(f"Connected database: {database}")
            print(f"Connected user: {current_user}")
            print(f"Server port: {server_port}")
            print(f"PostgreSQL version: {version.split(',')[0]}")

    print("PostgreSQL connection successful!")

except psycopg.Error as error:
    print(f"PostgreSQL connection failed: {error}")
