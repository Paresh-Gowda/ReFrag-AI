import psycopg2
import urllib.parse

def setup_postgres():
    host = "127.0.0.1"
    port = 8126
    user = "postgres"
    password = "hitesh@postgre"
    db_name = "refrag_ai"

    print(f"Connecting to PostgreSQL server at {host}:{port}...")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres",
            connect_timeout=5
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute("SELECT datname FROM pg_database WHERE datname = %s;", (db_name,))
        exists = cur.fetchone()
        
        if not exists:
            print(f"Database '{db_name}' does not exist. Creating now...")
            cur.execute(f'CREATE DATABASE "{db_name}";')
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to setup database: {e}")
        return False

if __name__ == "__main__":
    setup_postgres()
