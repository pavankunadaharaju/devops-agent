"""Pipeline failure analysis capability."""

from typing import Optional

from pipedoc.core import GitHub, LLM, Cache, error_window, calculate_reduction
from .base import Capability, Confidence, Finding, Result, Severity


class Analyze(Capability):
    """Diagnose GitHub Actions pipeline failures with AI."""

    def __init__(self, github: GitHub, llm: LLM, cache: Cache, run_url: str):
        """Initialize Analyze capability.
        
        Args:
            github: GitHub API client
            llm: LLM client
            cache: Cache manager
            run_url: GitHub Actions run URL
        """
        self.github = github
        self.llm = llm
        self.cache = cache
        self.run_url = run_url
        self._parsed_url = github.parse_url(run_url)

    @property
    def name(self) -> str:
        """Capability name."""
        return "analyze"

    @property
    def description(self) -> str:
        """Capability description."""
        return "Diagnose failed GitHub Actions pipeline runs with AI"

    def gather(self) -> str:
        """Fetch failed job logs from GitHub Actions run.
        
        Returns:
            Concatenated raw logs from all failed jobs
        """
        owner = self._parsed_url["owner"]
        repo = self._parsed_url["repo"]
        run_id = self._parsed_url["run_id"]

        # Get failed jobs
        failed = self.github.failed_jobs(owner, repo, run_id)
        if not failed:
            return "No failed jobs found in this run."

        # Fetch logs for each failed job
        logs = []
        for job in failed:
            try:
                log = self.github.job_log(owner, repo, job.job_id)
                logs.append(f"=== Job: {job.name} ===\n{log}\n")
            except Exception as e:
                logs.append(f"=== Job: {job.name} ===\nError fetching log: {e}\n")

        return "\n".join(logs)

    def distill(self, raw: str) -> tuple[str, dict]:
        """Extract error windows from raw logs.
        
        Args:
            raw: Raw concatenated logs
            
        Returns:
            Tuple of (filtered_text, metadata)
        """
        distilled = error_window(raw, context_lines=8, keep_last=40)
        metadata = {
            "reduction_pct": calculate_reduction(raw, distilled),
            "raw_chars": len(raw),
            "distilled_chars": len(distilled),
            "run_url": self.run_url,
        }
        return distilled, metadata

    def reason(self, distilled: str, metadata: dict) -> tuple[list[Finding], dict]:
        """Diagnose root cause using LLM with cache.
        
        Args:
            distilled: Filtered error windows
            metadata: Metadata from distill()
            
        Returns:
            Tuple of (findings, usage_dict)
        """
        # Check cache first
        cached_result = self.cache.get(distilled)
        if cached_result:
            result = cached_result["result"]
            findings = [
                Finding(
                    title=f["title"],
                    detail=f["detail"],
                    severity=Severity(f.get("severity", "med")),
                    suggested_fix=f.get("suggested_fix"),
                    confidence=Confidence(f.get("confidence", "medium")),
                    cached=True,
                )
                for f in result.get("findings", [])
            ]
            return findings, {"tokens_used": 0, "cost_usd": 0.0}

        # Cache miss - call LLM
        system_prompt = (
            "You are a senior DevOps engineer diagnosing CI pipeline failures. "
            "Analyze the error logs and provide a concise root cause analysis. "
            "Respond with valid JSON only (no markdown fences): "
            '{"root_cause": "...", "explanation": "...", "suggested_fix": "...", "confidence": "high|medium|low"}'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze these failed logs:\n\n{distilled}"},
        ]

        response_text, usage = self.llm.call(messages, temperature=0.2, max_tokens=600)

        # Parse response
        try:
            response_json = self.llm.parse_json(response_text)
        except Exception as e:
            return [
                Finding(
                    title="LLM Response Parse Error",
                    detail=f"Failed to parse LLM response: {e}",
                    severity=Severity.LOW,
                    confidence=Confidence.LOW,
                )
            ], {"tokens_used": usage.total_tokens, "cost_usd": self.llm.get_cost()}

        # Build findings
        findings = [
            Finding(
                title="Pipeline Failure Diagnosis",
                detail=(
                    f"**Root Cause:** {response_json.get('root_cause', 'Unknown')}\n\n"
                    f"**Explanation:** {response_json.get('explanation', '')}"
                ),
                severity=Severity.HIGH,
                suggested_fix=response_json.get("suggested_fix"),
                confidence=Confidence(response_json.get("confidence", "medium").lower()),
            )
        ]

        # Cache the result
        cache_data = {
            "findings": [
                {
                    "title": f.title,
                    "detail": f.detail,
                    "severity": f.severity.value,
                    "suggested_fix": f.suggested_fix,
                    "confidence": f.confidence.value,
                }
                for f in findings
            ]
        }
        self.cache.put(distilled, cache_data)

        return findings, {"tokens_used": usage.total_tokens, "cost_usd": self.llm.get_cost()}

    def act(self, result: Result) -> None:
        """Render findings to terminal and HTML report.
        
        Args:
            result: Result object
        """
        from pipedoc.render import render_result

        render_result(result)
