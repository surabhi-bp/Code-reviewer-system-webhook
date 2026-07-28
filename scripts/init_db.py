"""
Filename: scripts/init_db.py
Location: ai-code-reviewer/scripts/init_db.py
Action: Database Initializer Script

Description:
Imports the application context and database instance to construct all tables in the configured database target.
"""

import os
import sys

# Ensure project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
# Ensure all models are imported so SQLAlchemy registers them on metadata
from app.models import *

def initialize_database():
    """Create all configured database tables within Flask application context."""
    # Read environment setting or default to development
    env = os.getenv("FLASK_ENV", "development")
    print(f"Initializing database for env: {env}...")
    
    app = create_app(env)
    
    with app.app_context():
        # Relying on DATABASE_URL from config.py
        print(f"Target Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        db.create_all()
        print("Database tables initialized successfully!")

if __name__ == "__main__":
    initialize_database()
