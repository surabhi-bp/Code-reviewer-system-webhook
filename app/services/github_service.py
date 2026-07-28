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

    def post_pr_review(self, repo_name: str, pr_number: int, issues: list[dict]) -> dict:
        """
        Post a Pull Request review summary comment to GitHub.

        Args:
            repo_name: Full repository name (e.g. 'owner/repo').
            pr_number: Pull request number.
            issues: List of issue dictionaries containing findings.

        Returns:
            dict: JSON response from GitHub API for the created comment.

        Raises:
            Exception: If request fails or configuration is missing.
        """
        token = current_app.config.get("GITHUB_TOKEN")
        if not token:
            raise Exception("GITHUB_TOKEN is not configured in the application.")

        url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        header_str = "## Automated Code Review Summary\n\n"
        if not issues:
            body_str = header_str + "No code quality issues found! Great job!"
        else:
            table_rows = [
                "| File | Line | Category | Severity | Message |",
                "| :--- | :--- | :------- | :------- | :------ |"
            ]
            for issue in issues:
                file_path = issue.get("file_path") or issue.get("file") or "N/A"
                line_number = issue.get("line_number") if issue.get("line_number") is not None else issue.get("line", "N/A")
                category = issue.get("category", "N/A")
                severity = issue.get("severity", "N/A")
                message = issue.get("message", "")
                table_rows.append(f"| {file_path} | {line_number} | {category} | {severity} | {message} |")
            body_str = header_str + "\n".join(table_rows)

        try:
            response = requests.post(url, headers=headers, json={"body": body_str}, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to post PR review comment to GitHub: {str(e)}")

