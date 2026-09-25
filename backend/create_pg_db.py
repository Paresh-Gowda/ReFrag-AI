import os
import sys
import psycopg2
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:hitesh%40postgre@localhost:8126/refrag_ai")

def main():
    print(f"Connecting using DATABASE_URL: {DATABASE_URL}")
    try:
        parsed = urlparse(DATABASE_URL)
        user = unquote(parsed.username) if parsed.username else "postgres"
        password = unquote(parsed.password) if parsed.password else ""
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8126
        dbname = parsed.path.lstrip("/") or "refrag_ai"

        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres",
            connect_timeout=5
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database WHERE datname=%s;", (dbname,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f'CREATE DATABASE "{dbname}";')
                print(f"SUCCESS: Database '{dbname}' created in PostgreSQL 18!")
            else:
                print(f"SUCCESS: Database '{dbname}' already exists in PostgreSQL 18.")
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
