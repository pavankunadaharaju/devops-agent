"""Pull request review capability."""

from typing import Optional

from pipedoc.core import GitHub, LLM, Cache, diff_per_file, calculate_reduction
from .base import Capability, Confidence, Finding, Result, Severity


class Review(Capability):
    """AI-powered review of pull requests."""

    def __init__(self, github: GitHub, llm: LLM, cache: Cache, pr_url: str):
        """Initialize Review capability.
        
        Args:
            github: GitHub API client
            llm: LLM client
            cache: Cache manager
            pr_url: GitHub pull request URL
        """
        self.github = github
        self.llm = llm
        self.cache = cache
        self.pr_url = pr_url
        self._parsed_url = github.parse_url(pr_url)

    @property
    def name(self) -> str:
        """Capability name."""
        return "review"

    @property
    def description(self) -> str:
        """Capability description."""
        return "Review pull requests for bugs, security issues, and CI/K8s misconfigurations"

    def gather(self) -> str:
        """Fetch PR diff and metadata from GitHub.
        
        Returns:
            Formatted string with diff and metadata
        """
        owner = self._parsed_url["owner"]
        repo = self._parsed_url["repo"]
        pr_number = self._parsed_url["pr_number"]

        # Fetch diff
        diff = self.github.pr_diff(owner, repo, pr_number)

        # Fetch metadata
        meta = self.github.pr_meta(owner, repo, pr_number)

        # Combine
        combined = f"PR: {meta['title']}\nAuthor: {meta['author']}\nDescription: {meta.get('body', 'N/A')}\n\n--- DIFF ---\n{diff}"

        return combined

    def distill(self, raw: str) -> tuple[str, dict]:
        """Filter diffs: skip lock/vendor files, chunk per file.
        
        Args:
            raw: Raw combined diff + metadata
            
        Returns:
            Tuple of (filtered_text, metadata)
        """
        # Extract diff section
        diff_start = raw.find("--- DIFF ---")
        if diff_start == -1:
            metadata_part = raw
            diff_part = ""
        else:
            metadata_part = raw[:diff_start]
            diff_part = raw[diff_start + len("--- DIFF ---") :].strip()

        # Filter files
        file_diffs = diff_per_file(diff_part)

        # Reconstruct with only relevant diffs
        filtered_diffs = "\n".join([f["diff"] for f in file_diffs])
        distilled = f"{metadata_part}\n\n--- FILTERED DIFF ({len(file_diffs)} files) ---\n{filtered_diffs}"

        metadata = {
            "reduction_pct": calculate_reduction(raw, distilled),
            "raw_chars": len(raw),
            "distilled_chars": len(distilled),
            "file_count": len(file_diffs),
            "pr_url": self.pr_url,
        }

        return distilled, metadata

    def reason(self, distilled: str, metadata: dict) -> tuple[list[Finding], dict]:
        """Review code with LLM with cache.
        
        Args:
            distilled: Filtered diffs
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
                    title=f"{f.get('file', 'unknown')}:{f.get('line', '?')}",
                    detail=f["comment"],
                    severity=Severity(f.get("severity", "low")),
                    location=f"{f.get('file')}:{f.get('line')}",
                    cached=True,
                )
                for f in result.get("findings", [])
            ]
            return findings, {"tokens_used": 0, "cost_usd": 0.0}

        # Cache miss - call LLM
        system_prompt = (
            "You are a senior DevOps code reviewer. Analyze the provided diffs for: "
            "1. Bugs or logic errors\n"
            "2. Security vulnerabilities\n"
            "3. CI/Kubernetes misconfigurations\n"
            "4. Performance issues\n"
            "Respond with valid JSON only (no markdown fences): "
            '{"findings": [{"file": "...", "line": N, "severity": "high|med|low", "comment": "..."}]}'
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review this PR:\n\n{distilled}"},
        ]

        response_text, usage = self.llm.call(messages, temperature=0.2, max_tokens=800)

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
        findings = []
        for finding_data in response_json.get("findings", []):
            findings.append(
                Finding(
                    title=f"{finding_data.get('file', 'unknown')}:{finding_data.get('line', '?')}",
                    detail=finding_data.get("comment", ""),
                    severity=Severity(finding_data.get("severity", "low")),
                    location=f"{finding_data.get('file')}:{finding_data.get('line')}",
                )
            )

        # Cache the result
        cache_data = {
            "findings": [
                {
                    "file": f.location.split(":")[0] if f.location else "unknown",
                    "line": f.location.split(":")[1] if f.location and ":" in f.location else "?",
                    "severity": f.severity.value,
                    "comment": f.detail,
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
