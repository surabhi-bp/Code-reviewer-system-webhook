"""
Filename: app/services/github_service.py
Description: Service for interacting with GitHub REST API endpoints.
"""

import requests
from flask import current_app

class GitHubService:
    """Service to handle REST requests to the GitHub API."""

    def fetch_pr_diff(self, repo_name: str, pr_number: int) -> str:
        """
        Fetch the unified diff of a Pull Request from GitHub.
        
        Args:
            repo_name: Full repository name (e.g. 'owner/repo').
            pr_number: Pull request number.
            
        Returns:
            str: The raw diff content.
            
        Raises:
            Exception: If request fails or configuration is missing.
        """
        token = current_app.config.get("GITHUB_TOKEN")
        if not token:
            raise Exception("GITHUB_TOKEN is not configured in the application.")
            
        url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Pull Request diff from GitHub: {str(e)}")
