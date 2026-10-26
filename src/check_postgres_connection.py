
import getpass
import psycopg

password = getpass.getpass("Enter PostgreSQL password for postgres: ")

try:
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="nepal_data",
        user="postgres",
        password=password,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version();")
            database, version = cur.fetchone()

            print(f"Connected database: {database}")
            print(f"PostgreSQL version: {version.split(',')[0]}")

    print("PostgreSQL connection successful!")

except psycopg.Error as error:
    print(f"PostgreSQL connection failed: {error}")
