
import getpass
import os
import sys

import psycopg


def main() -> int:
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
                cur.execute(
                    """
                    SELECT
                        current_database(),
                        current_user,
                        inet_server_addr()::text,
                        inet_server_port(),
                        version();
                    """
                )

                database, current_user, server_address, server_port, version = (
                    cur.fetchone()
                )

                print(f"Connected database: {database}")
                print(f"Connected user: {current_user}")
                print(f"Server address: {server_address}")
                print(f"Server port: {server_port}")
                print(f"PostgreSQL version: {version.split(',')[0]}")

        print("PostgreSQL connection successful!")
        return 0

    except psycopg.Error as error:
        print(
            f"PostgreSQL connection failed: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
