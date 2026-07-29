"""
Filename: app/services/review_orchestrator.py
Description: Service for orchestrating end-to-end PR code reviews.
"""

import time
import zlib
from typing import Optional, Dict, Any, List
from flask import current_app

from app.extensions import db
from app.models import (
    Organization,
    Repository,
    PullRequest,
    ReviewRun,
    ReviewIssue,
)
from app.services.github_service import GitHubService
from app.services.code_parser import CodeParserService
from app.services.ai_engine import AIEngineService
from app.services.ai.gemini_provider import GeminiProvider


class ReviewOrchestratorService:
    """Orchestrates fetching PR diffs, running AI analysis, saving findings,
    and posting review comments.
    """

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        code_parser_service: Optional[CodeParserService] = None,
        ai_engine_service: Optional[AIEngineService] = None,
        ai_provider: Optional[Any] = None,
    ):
        self.github_service = github_service or GitHubService()
        self.code_parser_service = code_parser_service or CodeParserService()
        self.ai_engine_service = ai_engine_service or AIEngineService()
        self.ai_provider = ai_provider or GeminiProvider()

    def process_pull_request(
        self,
        repo_name: str,
        pr_number: int,
        webhook_payload: Optional[Dict[str, Any]] = None,
    ) -> ReviewRun:
        """Process an incoming PR review workflow.

        Args:
            repo_name: Full repository name (e.g. 'owner/repo').
            pr_number: Pull request number.
            webhook_payload: Optional webhook payload dictionary from GitHub.

        Returns:
            ReviewRun: The persisted ReviewRun database object.
        """
        start_time = time.time()
        payload = webhook_payload or {}
        repo_data = (
            payload.get("repository", {})
            if isinstance(payload, dict)
            else {}
        )
        owner_data = (
            repo_data.get("owner", {})
            if isinstance(repo_data, dict)
            else {}
        )
        pr_data = (
            payload.get("pull_request", {})
            if isinstance(payload, dict)
            else {}
        )

        review_run: Optional[ReviewRun] = None

        try:
            # 1. Parse Organization details
            parts = repo_name.split("/", 1)
            org_name = parts[0]
            github_org_id = (
                owner_data.get("id", 0)
                if isinstance(owner_data, dict)
                else 0
            )

            org = None
            if github_org_id:
                org = Organization.query.filter_by(
                    github_org_id=github_org_id
                ).first()
            if not org:
                org = Organization.query.filter_by(name=org_name).first()
            if not org:
                fallback_org_id = (
                    github_org_id
                    or zlib.crc32(org_name.encode("utf-8"))
                    or 1
                )
                org = Organization(
                    github_org_id=fallback_org_id,
                    name=org_name,
                )
                db.session.add(org)
                db.session.flush()

            # 2. Parse Repository details
            repo_short_name = parts[1] if len(parts) > 1 else repo_name
            if isinstance(repo_data, dict) and repo_data.get("name"):
                repo_short_name = repo_data.get("name")
            github_repo_id = (
                repo_data.get("id", 0)
                if isinstance(repo_data, dict)
                else 0
            )

            repo = None
            if github_repo_id:
                repo = Repository.query.filter_by(
                    github_repo_id=github_repo_id
                ).first()
            if not repo:
                repo = Repository.query.filter_by(
                    organization_id=org.id, name=repo_short_name
                ).first()
            if not repo:
                fallback_repo_id = (
                    github_repo_id
                    or zlib.crc32(
                        f"{org_name}/{repo_short_name}".encode("utf-8")
                    )
                    or 1
                )
                repo = Repository(
                    organization_id=org.id,
                    github_repo_id=fallback_repo_id,
                    name=repo_short_name,
                )
                db.session.add(repo)
                db.session.flush()

            # 3. Parse PullRequest details
            pr_title = (
                pr_data.get("title") if isinstance(pr_data, dict) else None
            )
            if not pr_title:
                pr_title = f"Pull Request #{pr_number}"
            pr_state = (
                pr_data.get("state") if isinstance(pr_data, dict) else None
            )
            if not pr_state:
                pr_state = "open"

            pr = PullRequest.query.filter_by(
                repository_id=repo.id, github_pr_number=pr_number
            ).first()
            if not pr:
                pr = PullRequest(
                    repository_id=repo.id,
                    github_pr_number=pr_number,
                    title=pr_title,
                    state=pr_state,
                )
                db.session.add(pr)
                db.session.flush()
            else:
                pr.title = pr_title
                pr.state = pr_state

            db.session.commit()

            # 4. Model name and commit SHA
            commit_sha = (
                pr_data.get("head", {}).get("sha")
                if isinstance(pr_data, dict)
                and isinstance(pr_data.get("head"), dict)
                else None
            )
            if not commit_sha:
                commit_sha = "unknown"

            try:
                model_name = current_app.config.get(
                    "MODEL_NAME", "gemini-2.5-flash"
                )
            except Exception:
                model_name = "gemini-2.5-flash"

            review_run = ReviewRun(
                pull_request_id=pr.id,
                commit_sha=commit_sha[:40],
                model_name=model_name,
                status="queued",
            )
            db.session.add(review_run)
            db.session.commit()

            # 5. Perform Review & Post Results
            diff_content = self.github_service.fetch_pr_diff(
                repo_name, pr_number
            )
            parsed_files = self.code_parser_service.parse_diff(diff_content)

            all_issues: List[Dict[str, Any]] = []

            for file_info in parsed_files:
                file_path = file_info.get("file_path", "")
                patch_content = file_info.get("patch", "")

                issues = self.ai_engine_service.analyze_code(
                    file_path, patch_content, self.ai_provider
                )

                for issue in issues:
                    issue_file_path = (
                        issue.get("file_path")
                        or issue.get("file")
                        or file_path
                    )
                    raw_line = (
                        issue.get("line_number")
                        if issue.get("line_number") is not None
                        else issue.get("line", 0)
                    )
                    try:
                        line_num = int(raw_line) if raw_line is not None else 0
                    except (ValueError, TypeError):
                        line_num = 0

                    category = issue.get("category", "general")
                    severity = issue.get("severity", "info")
                    message = issue.get("message", "")

                    issue_record = ReviewIssue(
                        review_run_id=review_run.id,
                        file_path=issue_file_path,
                        line_number=line_num,
                        category=category,
                        severity=severity,
                        message=message,
                    )
                    db.session.add(issue_record)

                    all_issues.append(
                        {
                            "file_path": issue_file_path,
                            "line_number": line_num,
                            "category": category,
                            "severity": severity,
                            "message": message,
                        }
                    )

            self.github_service.post_pr_review(
                repo_name, pr_number, all_issues
            )

            review_run.status = "completed"
            review_run.duration_sec = round(time.time() - start_time, 2)
            db.session.commit()

            return review_run

        except Exception as e:
            db.session.rollback()
            if review_run:
                review_run.status = "failed"
                review_run.error_message = str(e)
                review_run.duration_sec = round(time.time() - start_time, 2)
                db.session.add(review_run)
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
            raise e
