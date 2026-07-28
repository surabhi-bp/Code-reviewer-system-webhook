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
