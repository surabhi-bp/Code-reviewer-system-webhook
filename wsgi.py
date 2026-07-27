"""
Filename: wsgi.py
Location: ai-code-reviewer/wsgi.py
Action: Production Entry Point

Description:
WSGI entry point for launching the application under Gunicorn or Flask CLI.
"""

import os
from app import create_app

# Fetch environment setting or default to development
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
