import sys
import psycopg2

ports = [5432, 5433, 5434]
passwords = ["postgres", "root", "admin", "1234", "password", "123456", ""]

print("Testing PostgreSQL ports and credentials...")

for port in ports:
    for pwd in passwords:
        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                port=port,
                user="postgres",
                password=pwd,
                dbname="postgres",
                connect_timeout=2
            )
            print(f"SUCCESS! Connected to PostgreSQL on port {port} with password '{pwd}'")
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT datname FROM pg_database WHERE datname='refrag_ai';")
                exists = cur.fetchone()
                if not exists:
                    print("Creating database 'refrag_ai'...")
                    cur.execute("CREATE DATABASE refrag_ai;")
                    print("Database 'refrag_ai' created successfully!")
                else:
                    print("Database 'refrag_ai' already exists.")
            conn.close()
            sys.exit(0)
        except Exception as e:
            print(f"Port {port}, pwd '{pwd}': {e}")
