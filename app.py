import os
from flask import Flask
from dotenv import load_dotenv
from models import db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.volunteer import volunteer_bp
from routes.participant import participant_bp
from routes.api import api_bp

from flask_cors import CORS

load_dotenv()


def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'techxora26-dev-key')
    
    # Use Supabase PostgreSQL or fallback to local SQLite for dev
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///techxora26.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'admin123')
    app.config['VOLUNTEER_PASSWORD'] = os.getenv('VOLUNTEER_PASSWORD', 'volunteer123')

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(volunteer_bp, url_prefix='/volunteer')
    app.register_blueprint(participant_bp, url_prefix='/participant')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/init-db')
    def init_db():
        try:
            db.create_all()
            return "Database initialized successfully!", 200
        except Exception as e:
            return f"Error: {str(e)}", 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
