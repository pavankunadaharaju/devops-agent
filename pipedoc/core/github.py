"""GitHub API client for pipedoc."""

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import requests


@dataclass
class FailedJob:
    """Represents a failed job in a GitHub Actions run."""

    job_id: int
    name: str
    conclusion: str
    url: str


class GitHub:
    """GitHub REST API client for fetching pipeline and PR data."""

    BASE_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"

    def __init__(self, token: str):
        """Initialize GitHub client.
        
        Args:
            token: GitHub personal access token (PAT)
        """
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": self.API_VERSION,
            "Accept": "application/vnd.github+json",
        }

    def parse_url(self, url: str) -> dict:
        """Parse GitHub URL to extract owner, repo, and resource ID.
        
        Args:
            url: GitHub URL (action run or PR)
            
        Returns:
            dict with owner, repo, run_id (for actions) or pr_number (for PRs)
        """
        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")

        owner = path_parts[0]
        repo = path_parts[1]

        # Parse action run URL
        if "actions/runs" in url:
            match = re.search(r"/actions/runs/(\d+)", url)
            if match:
                return {"owner": owner, "repo": repo, "run_id": int(match.group(1))}

        # Parse PR URL
        if "pull" in url:
            match = re.search(r"/pull/(\d+)", url)
            if match:
                return {"owner": owner, "repo": repo, "pr_number": int(match.group(1))}

        raise ValueError(f"Could not parse GitHub URL: {url}")

    def failed_jobs(self, owner: str, repo: str, run_id: int) -> list[FailedJob]:
        """Fetch failed jobs from a GitHub Actions run.
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: GitHub Actions run ID
            
        Returns:
            List of FailedJob objects
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        failed = []
        for job in data.get("jobs", []):
            if job.get("conclusion") == "failure":
                failed.append(
                    FailedJob(
                        job_id=job["id"],
                        name=job["name"],
                        conclusion=job["conclusion"],
                        url=job["html_url"],
                    )
                )
        return failed

    def job_log(self, owner: str, repo: str, job_id: int) -> str:
        """Fetch raw log for a GitHub Actions job.
        
        Args:
            owner: Repository owner
            repo: Repository name
            job_id: GitHub Actions job ID
            
        Returns:
            Raw job log text
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/actions/jobs/{job_id}/logs"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetch unified diff for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Unified diff text
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.diff"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def pr_meta(self, owner: str, repo: str, pr_number: int) -> dict:
        """Fetch metadata for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            dict with title, description, author, etc.
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        return {
            "title": data.get("title"),
            "body": data.get("body"),
            "author": data.get("user", {}).get("login"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "state": data.get("state"),
            "commits": data.get("commits"),
            "changed_files": data.get("changed_files"),
            "additions": data.get("additions"),
            "deletions": data.get("deletions"),
            "html_url": data.get("html_url"),
        }

    def connectivity_check(self) -> bool:
        """Verify GitHub Models API connectivity with current token.
        
        Returns:
            True if connectivity is working, False otherwise
        """
        try:
            url = "https://models.github.ai/inference/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "openai/gpt-4.1",
                "messages": [{"role": "user", "content": "say hi"}],
                "max_tokens": 10,
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.status_code in [200, 201]
        except Exception:
            return False
