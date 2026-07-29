import pytest
from unittest.mock import MagicMock
from app import create_app
from app.extensions import db
from app.models import Organization, Repository, PullRequest, ReviewRun, ReviewIssue
from app.services.review_orchestrator import ReviewOrchestratorService


@pytest.fixture
def app_ctx():
    app = create_app("development")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_process_pull_request_success(app_ctx):
    mock_github = MagicMock()
    mock_github.fetch_pr_diff.return_value = "+++ b/main.py\n+print('hello')"
    mock_github.post_pr_review.return_value = {"id": 100}

    mock_code_parser = MagicMock()
    mock_code_parser.parse_diff.return_value = [
        {"file_path": "main.py", "patch": "+print('hello')"}
    ]

    mock_ai_engine = MagicMock()
    mock_ai_engine.analyze_code.return_value = [
        {
            "category": "lint",
            "severity": "low",
            "line_number": "1",
            "message": "Use double quotes for consistency"
        }
    ]

    mock_provider = MagicMock()

    orchestrator = ReviewOrchestratorService(
        github_service=mock_github,
        code_parser_service=mock_code_parser,
        ai_engine_service=mock_ai_engine,
        ai_provider=mock_provider,
    )

    webhook_payload = {
        "repository": {
            "id": 101,
            "name": "my-repo",
            "owner": {"id": 201, "login": "my-org"}
        },
        "pull_request": {
            "number": 5,
            "title": "Fix bug",
            "state": "open",
            "head": {"sha": "1234567890abcdef1234567890abcdef12345678"}
        }
    }

    review_run = orchestrator.process_pull_request(
        repo_name="my-org/my-repo",
        pr_number=5,
        webhook_payload=webhook_payload
    )

    assert review_run.status == "completed"
    assert review_run.commit_sha == "1234567890abcdef1234567890abcdef12345678"
    assert review_run.duration_sec is not None
    assert review_run.duration_sec >= 0.0

    org = Organization.query.filter_by(name="my-org").first()
    assert org is not None
    assert org.github_org_id == 201

    repo = Repository.query.filter_by(name="my-repo").first()
    assert repo is not None
    assert repo.github_repo_id == 101

    pr = PullRequest.query.filter_by(github_pr_number=5).first()
    assert pr is not None
    assert pr.title == "Fix bug"

    issues = ReviewIssue.query.filter_by(review_run_id=review_run.id).all()
    assert len(issues) == 1
    assert issues[0].file_path == "main.py"
    assert issues[0].line_number == 1
    assert issues[0].category == "lint"
    assert issues[0].severity == "low"

    mock_github.fetch_pr_diff.assert_called_once_with("my-org/my-repo", 5)
    mock_github.post_pr_review.assert_called_once()
    posted_issues = mock_github.post_pr_review.call_args[0][2]
    assert posted_issues[0]["line_number"] == 1


def test_process_pull_request_failure_handling(app_ctx):
    mock_github = MagicMock()
    mock_github.fetch_pr_diff.side_effect = Exception("GitHub API down")

    mock_code_parser = MagicMock()
    mock_ai_engine = MagicMock()
    mock_provider = MagicMock()

    orchestrator = ReviewOrchestratorService(
        github_service=mock_github,
        code_parser_service=mock_code_parser,
        ai_engine_service=mock_ai_engine,
        ai_provider=mock_provider,
    )

    with pytest.raises(Exception, match="GitHub API down"):
        orchestrator.process_pull_request(repo_name="my-org/my-repo", pr_number=10)

    pr = PullRequest.query.filter_by(github_pr_number=10).first()
    assert pr is not None

    review_run = ReviewRun.query.filter_by(pull_request_id=pr.id).first()
    assert review_run is not None
    assert review_run.status == "failed"
    assert "GitHub API down" in review_run.error_message
    assert review_run.duration_sec is not None


def test_process_pull_request_without_payload(app_ctx):
    mock_github = MagicMock()
    mock_github.fetch_pr_diff.return_value = ""
    mock_github.post_pr_review.return_value = {}

    mock_code_parser = MagicMock()
    mock_code_parser.parse_diff.return_value = []
    mock_ai_engine = MagicMock()
    mock_provider = MagicMock()

    orchestrator = ReviewOrchestratorService(
        github_service=mock_github,
        code_parser_service=mock_code_parser,
        ai_engine_service=mock_ai_engine,
        ai_provider=mock_provider,
    )

    review_run = orchestrator.process_pull_request(
        repo_name="demo-owner/demo-repo",
        pr_number=1
    )

    assert review_run.status == "completed"
    assert review_run.commit_sha == "unknown"

    org = Organization.query.filter_by(name="demo-owner").first()
    assert org is not None
    assert org.github_org_id > 0

    repo = Repository.query.filter_by(name="demo-repo").first()
    assert repo is not None
    assert repo.github_repo_id > 0


def test_review_orchestrator_default_ai_provider_and_model_fallback(app_ctx):
    from app.services.ai.gemini_provider import GeminiProvider

    mock_github = MagicMock()
    mock_github.fetch_pr_diff.return_value = ""
    mock_github.post_pr_review.return_value = {}

    mock_code_parser = MagicMock()
    mock_code_parser.parse_diff.return_value = []
    mock_ai_engine = MagicMock()

    orchestrator = ReviewOrchestratorService(
        github_service=mock_github,
        code_parser_service=mock_code_parser,
        ai_engine_service=mock_ai_engine,
    )

    assert isinstance(orchestrator.ai_provider, GeminiProvider)

    review_run = orchestrator.process_pull_request(
        repo_name="default-org/default-repo",
        pr_number=99
    )
    assert review_run.model_name == "gemini-1.5-flash"

