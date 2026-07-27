"""
Filename: app/api/v1/analytics.py
Location: ai-code-reviewer/app/api/v1/analytics.py
Action: Analytics Dashboard API Blueprint

Description:
Provides REST API endpoints for fetching review metrics and dashboard stats.
"""

from flask import Blueprint, jsonify

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Return overview metrics for dashboard visualizations."""
    return jsonify({
        'total_reviews': 0,
        'bugs_detected': 0,
        'security_issues': 0,
        'average_review_time_sec': 0.0
    }), 200
