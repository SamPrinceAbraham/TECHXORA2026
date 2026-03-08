import os
from flask import Flask
from models import db
from dotenv import load_dotenv

load_dotenv()

def migrate():
    app = Flask(__name__)
    
    # Use Supabase PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    if not database_url:
        print("DATABASE_URL not found in environment.")
        return

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("Initializing Supabase database schema...")
        db.create_all()
        print("Success! Tables created in Supabase.")

if __name__ == "__main__":
    migrate()
