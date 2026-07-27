"""
Filename: app/__init__.py
Location: ai-code-reviewer/app/__init__.py
Action: Application Factory Init

Description:
Implements the Application Factory pattern to construct Flask app instances.
"""

from flask import Flask
from config import config
from app.extensions import db

def create_app(config_name='development'):
    """Construct and configure the Flask application instance."""
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
