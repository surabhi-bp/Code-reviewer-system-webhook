"""
Filename: app/extensions.py
Location: ai-code-reviewer/app/extensions.py
Action: Centralized Flask Extensions

Description:
Instantiates Flask extensions globally without binding to an app instance,
preventing circular imports.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
