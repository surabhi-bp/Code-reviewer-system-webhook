"""
Filename: setup_workspace.py
Location: ai-code-reviewer/
Action: Create file and replace contents.

Description:
Automated workspace setup script to build enterprise directory layout, 
virtual environment instructions, dependency files, and base configurations.
"""

import os
import sys

# Define all required project directories
DIRECTORIES = [
    "app",
    "app/api",
    "app/api/v1",
    "app/services",
    "app/models",
    "app/static",
    "app/static/css",
    "app/static/js",
    "app/templates",
    "tests",
    "scripts",
    "logs",
]

# Define base files with initial content
FILES = {
    ".gitignore": """# Python Environment
venv/
__pycache__/
*.py[cod]
*$py.class

# Environment variables
.env
.env.local

# Database
*.sqlite
*.db

# IDE & OS
.vscode/
.idea/
.DS_Store

# Logs
logs/*.log
""",
    ".env.example": """# Flask Application Settings
FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=generate_a_secure_random_key_here

# Database Configuration
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/code_review_db

# GitHub Integration
GITHUB_TOKEN=ghp_your_personal_access_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_hmac_secret_here

# AI Model Configuration
MODEL_NAME=codellama:python
OLLAMA_BASE_URL=http://localhost:11434
""",
    "requirements.txt": """flask==3.0.2
gunicorn==21.2.0
flask-sqlalchemy==3.1.1
pymysql==1.1.0
cryptography==42.0.5
python-dotenv==1.0.1
requests==2.31.0
pyjwt==2.8.0
ollama==0.1.7
chartjs-python==0.1.1
pytest==8.1.1
""",
    "config.py": """\"\"\"
Filename: config.py
Location: ai-code-reviewer/config.py
Action: Base Configuration Module

Description:
Centralized environment configuration management following 
Twelve-Factor App methodologies.
\"\"\"

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    \"\"\"Base configuration class with common settings.\"\"\"
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-dev-secret-key-12345')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    MODEL_NAME = os.getenv('MODEL_NAME', 'codellama:python')

class DevelopmentConfig(Config):
    \"\"\"Development environment configuration.\"\"\"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:password@localhost:3306/code_review_db'
    )

class ProductionConfig(Config):
    \"\"\"Production environment configuration.\"\"\"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

# Configuration Map
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
""",
    "wsgi.py": """\"\"\"
Filename: wsgi.py
Location: ai-code-reviewer/wsgi.py
Action: Production Entry Point

Description:
WSGI entry point for launching the application under Gunicorn or Flask CLI.
\"\"\"

import os
from app import create_app

# Fetch environment setting or default to development
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
""",
    "app/__init__.py": """\"\"\"
Filename: app/__init__.py
Location: ai-code-reviewer/app/__init__.py
Action: Application Factory Init

Description:
Implements the Application Factory pattern to construct Flask app instances.
\"\"\"

from flask import Flask
from config import config
from app.extensions import db

def create_app(config_name='development'):
    \"\"\"Construct and configure the Flask application instance.\"\"\"
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register API Blueprints
    from app.api.v1.webhooks import webhooks_bp
    from app.api.v1.analytics import analytics_bp
    
    app.register_blueprint(webhooks_bp, url_prefix='/api/v1/webhooks')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'AI Code Review Assistant'}, 200
        
    return app
""",
    "app/extensions.py": """\"\"\"
Filename: app/extensions.py
Location: ai-code-reviewer/app/extensions.py
Action: Centralized Flask Extensions

Description:
Instantiates Flask extensions globally without binding to an app instance,
preventing circular imports.
\"\"\"

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
""",
    "app/api/v1/__init__.py": "",
    "app/api/v1/webhooks.py": """\"\"\"
Filename: app/api/v1/webhooks.py
Location: ai-code-reviewer/app/api/v1/webhooks.py
Action: Webhook Blueprint Endpoint

Description:
Receives, validates, and routes incoming GitHub webhook HTTP POST requests.
\"\"\"

from flask import Blueprint, request, jsonify

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/github', methods=['POST'])
def handle_github_webhook():
    \"\"\"Receive and process GitHub Pull Request events.\"\"\"
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    
    # Placeholder response for setup validation
    return jsonify({
        'message': 'Webhook received successfully',
        'event': event_type
    }), 202
""",
    "app/api/v1/analytics.py": """\"\"\"
Filename: app/api/v1/analytics.py
Location: ai-code-reviewer/app/api/v1/analytics.py
Action: Analytics Dashboard API Blueprint

Description:
Provides REST API endpoints for fetching review metrics and dashboard stats.
\"\"\"

from flask import Blueprint, jsonify

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    \"\"\"Return overview metrics for dashboard visualizations.\"\"\"
    return jsonify({
        'total_reviews': 0,
        'bugs_detected': 0,
        'security_issues': 0,
        'average_review_time_sec': 0.0
    }), 200
""",
    "app/services/__init__.py": "",
    "app/models/__init__.py": "",
}

def build_workspace():
    print("==================================================")
    print(" Starting Enterprise Workspace Setup...")
    print("==================================================")
    
    # Create Directories
    for directory in DIRECTORIES:
        os.makedirs(directory, exist_ok=True)
        print(f" [+] Created directory: {directory}")
        
    # Create Files
    for filepath, content in FILES.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f" [+] Created file: {filepath}")
        
    # Generate local .env from .env.example if not existing
    if not os.path.exists(".env"):
        with open(".env", "w", encoding="utf-8") as f:
            with open(".env.example", "r", encoding="utf-8") as ex:
                f.write(ex.read())
        print(" [+] Created local .env configuration from template.")
        
    print("\n[SUCCESS] Enterprise Workspace Initialized!")

if __name__ == "__main__":
    build_workspace()