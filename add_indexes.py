import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())

from app import create_app
from models import db

app = create_app()

def run_migration():
    with app.app_context():
        queries = [
            "CREATE INDEX IF NOT EXISTS ix_logs_participant_id ON logs (participant_id);",
            "CREATE INDEX IF NOT EXISTS ix_logs_action ON logs (action);",
            "CREATE INDEX IF NOT EXISTS ix_logs_timestamp ON logs (timestamp);"
        ]
        
        for q in queries:
            try:
                db.session.execute(text(q))
                db.session.commit()
                print(f"Executed: {q}")
            except Exception as e:
                db.session.rollback()
                print(f"Note (might already exist or dialect doesn't support IF NOT EXISTS): {e}")

if __name__ == "__main__":
    run_migration()
    print("Migration complete.")
