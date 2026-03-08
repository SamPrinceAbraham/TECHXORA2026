import os
import sys
from dotenv import load_dotenv
from app import create_app
from models import db, Team, Participant, Payment, Log
from supabase_manager import supabase

load_dotenv()

def reset_system():
    print("⚠️  WARNING: This will delete ALL registrations, payments, and files (QR codes/ID cards).")
    confirm = input("Are you absolutely sure? (type 'RESET' to confirm): ")
    
    if confirm != 'RESET':
        print("Reset cancelled.")
        return

    app = create_app()
    with app.app_context():
        print("\n1. Clearing Database Tables...")
        try:
            # Delete in order of foreign key dependencies
            db.session.query(Log).delete()
            db.session.query(Payment).delete()
            db.session.query(Participant).delete()
            db.session.query(Team).delete()
            
            # Reset problem statement counts
            from models import ProblemStatement
            problems = ProblemStatement.query.all()
            for p in problems:
                p.teams_selected = 0
            
            db.session.commit()
            print("✓ Database cleared.")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Database error: {e}")

        print("\n2. Clearing Supabase Storage...")
        if not supabase:
            print("✗ Supabase client not initialized. Skipping storage cleanup.")
        else:
            buckets = ['qrcodes', 'id_cards', 'proofs']
            for bucket in buckets:
                try:
                    print(f"  Cleaning bucket: {bucket}...")
                    # List all files
                    files = supabase.storage.from_(bucket).list()
                    if files:
                        file_names = [f['name'] for f in files]
                        # Bulk delete
                        supabase.storage.from_(bucket).remove(file_names)
                        print(f"  ✓ {len(file_names)} files deleted from {bucket}.")
                    else:
                        print(f"  ✓ {bucket} is already empty.")
                except Exception as e:
                    print(f"  ✗ Error cleaning {bucket}: {e}")

    print("\n✅ System Reset Complete! The hackathon is ready for a fresh start.")

if __name__ == "__main__":
    reset_system()
