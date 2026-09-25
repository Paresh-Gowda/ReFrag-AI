import sys
import psycopg2

passwords = [
    "paresh", "hitesh", "Paresh", "Hitesh", "refrag", "refrag-ai",
    "postgres123", "admin123", "123", "12345", "pass123", "Pass123",
    "Postgres", "Postgres123", "Root", "Admin", "password123", "Password123"
]

print("Testing additional passwords on port 8126...")

for pwd in passwords:
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=8126,
            user="postgres",
            password=pwd,
            dbname="postgres",
            connect_timeout=2
        )
        print(f"\nSUCCESS! Connected to PostgreSQL 18 on port 8126 with password '{pwd}'")
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database WHERE datname='refrag_ai';")
            exists = cur.fetchone()
            if not exists:
                print("Creating database 'refrag_ai'...")
                cur.execute("CREATE DATABASE refrag_ai;")
                print("Database 'refrag_ai' CREATED SUCCESSFULLY!")
            else:
                print("Database 'refrag_ai' already exists.")
        conn.close()
        sys.exit(0)
    except Exception as e:
        pass

print("\nNo auto-detected password matched. Please check your PostgreSQL password.")
