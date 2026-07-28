import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.services.github_service import GitHubService

def test_fetch_pr_diff_success():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = "fake-github-token"
    
    with app.app_context():
        service = GitHubService()
        
        with patch("app.services.github_service.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.text = "diff --git a/file.txt b/file.txt"
            mock_get.return_value = mock_response
            
            diff = service.fetch_pr_diff("owner/repo", 123)
            
            assert diff == "diff --git a/file.txt b/file.txt"
            mock_get.assert_called_once_with(
                "https://api.github.com/repos/owner/repo/pulls/123",
                headers={
                    "Authorization": "Bearer fake-github-token",
                    "Accept": "application/vnd.github.v3.diff"
                },
                timeout=10
            )

def test_fetch_pr_diff_http_error():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = "fake-github-token"
    
    with app.app_context():
        service = GitHubService()
        
        with patch("app.services.github_service.requests.get") as mock_get:
            from requests.exceptions import HTTPError
            mock_get.side_effect = HTTPError("Not Found")
            
            with pytest.raises(Exception) as exc_info:
                service.fetch_pr_diff("owner/repo", 123)
            assert "Failed to fetch Pull Request diff" in str(exc_info.value)


def test_post_pr_review_success():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = "fake-github-token"
    
    with app.app_context():
        service = GitHubService()
        issues = [
            {
                "file_path": "app/main.py",
                "line_number": 12,
                "category": "security",
                "severity": "high",
                "message": "Prevent SQL injection by parameterized statements."
            }
        ]
        
        with patch("app.services.github_service.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {"id": 1, "body": "comment"}
            mock_post.return_value = mock_response
            
            res = service.post_pr_review("owner/repo", 123, issues)
            
            assert res == {"id": 1, "body": "comment"}
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "https://api.github.com/repos/owner/repo/issues/123/comments"
            assert kwargs["headers"] == {
                "Authorization": "Bearer fake-github-token",
                "Accept": "application/vnd.github.v3+json"
            }
            assert kwargs["timeout"] == 10
            expected_body = (
                "## Automated Code Review Summary\n\n"
                "| File | Line | Category | Severity | Message |\n"
                "| :--- | :--- | :------- | :------- | :------ |\n"
                "| app/main.py | 12 | security | high | Prevent SQL injection by parameterized statements. |"
            )
            assert kwargs["json"] == {"body": expected_body}


def test_post_pr_review_no_issues_success():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = "fake-github-token"
    
    with app.app_context():
        service = GitHubService()
        
        with patch("app.services.github_service.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {"id": 2, "body": "no issues comment"}
            mock_post.return_value = mock_response
            
            res = service.post_pr_review("owner/repo", 123, [])
            
            assert res == {"id": 2, "body": "no issues comment"}
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            expected_body = "## Automated Code Review Summary\n\nNo code quality issues found! Great job!"
            assert kwargs["json"] == {"body": expected_body}


def test_post_pr_review_failure():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = "fake-github-token"
    
    with app.app_context():
        service = GitHubService()
        
        with patch("app.services.github_service.requests.post") as mock_post:
            from requests.exceptions import HTTPError
            mock_post.side_effect = HTTPError("API rate limit exceeded")
            
            with pytest.raises(Exception) as exc_info:
                service.post_pr_review("owner/repo", 123, [])
            assert "Failed to post PR review comment to GitHub" in str(exc_info.value)


def test_post_pr_review_missing_token():
    app = Flask("test_app")
    app.config["GITHUB_TOKEN"] = None
    
    with app.app_context():
        service = GitHubService()
        with pytest.raises(Exception) as exc_info:
            service.post_pr_review("owner/repo", 123, [])
        assert "GITHUB_TOKEN is not configured" in str(exc_info.value)


