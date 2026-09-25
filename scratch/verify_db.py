import sys
import os

# Dynamically resolve project_root and backend_dir relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
backend_dir = os.path.join(project_root, "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.chdir(backend_dir)

try:
    from app.config import settings
    from app.db.database import engine, Base, SessionLocal, DATABASE_URL
    from app.models.forensic import ForensicCase, ForensicArtifact
except ImportError:
    from backend.app.config import settings
    from backend.app.db.database import engine, Base, SessionLocal, DATABASE_URL
    from backend.app.models.forensic import ForensicCase, ForensicArtifact
from sqlalchemy import text

def verify():
    print("==================================================")
    print("      DATABASE CONNECTION DIAGNOSTIC & VERIFICATION ")
    print("==================================================")
    
    print(f"Configured DATABASE_URL : {settings.DATABASE_URL}")
    print(f"Active Engine Dialect   : {engine.dialect.name.upper()}")
    print(f"Active Database Driver  : {engine.driver}")
    print(f"Active Connection URL   : {engine.url}")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"Ping Test (SELECT 1)    : SUCCESS (Returned {result})")
    except Exception as e:
        print(f"Ping Test (SELECT 1)    : FAILED ({e})")
        return

    # Check tables & records count
    session = SessionLocal()
    try:
        cases_count = session.query(ForensicCase).count()
        artifacts_count = session.query(ForensicArtifact).count()
        print("\n--- DATABASE CONTENT METRICS ---")
        print(f"Total Forensic Cases Ingested      : {cases_count}")
        print(f"Total Forensic Artifacts Saved     : {artifacts_count}")

        if cases_count > 0:
            print("\n--- INGESTED FORENSIC CASES ---")
            for c in session.query(ForensicCase).order_by(ForensicCase.created_at.desc()).limit(5):
                print(f"  • Case [{c.id}] '{c.case_name}'")
                print(f"    - Files: {c.total_files} | Size: {c.total_size} bytes | Status: {c.status}")

        if artifacts_count > 0:
            print("\n--- SAMPLE INGESTED ARTIFACT EVIDENCE TRAIL ---")
            for a in session.query(ForensicArtifact).order_by(ForensicArtifact.created_at.desc()).limit(5):
                print(f"  • Artifact [{a.id[:8]}] Path: '{a.relative_path}'")
                print(f"    - SHA-256: {a.sha256_hash}")
                print(f"    - Magic Signature: {a.magic_signature}")
                print(f"    - MIME: {a.mime_type} | Size: {a.file_size} bytes | Is Duplicate: {a.is_duplicate}")

    except Exception as e:
        print(f"Query Error: {e}")
    finally:
        session.close()

    print("==================================================")

if __name__ == "__main__":
    verify()
