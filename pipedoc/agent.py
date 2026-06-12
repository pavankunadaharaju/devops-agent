"""Agent orchestrator for pipedoc."""

import os
from typing import Optional

from pipedoc.core import GitHub, LLM, Cache
from pipedoc.capabilities import Analyze, Review


class Agent:
    """Orchestrates GitHub client, LLM, cache, and capabilities."""

    def __init__(
        self,
        github_token: Optional[str] = None,
        model: Optional[str] = None,
        cache_path: Optional[str] = None,
    ):
        """Initialize Agent.
        
        Args:
            github_token: GitHub PAT (default from $GITHUB_TOKEN)
            model: LLM model name (default openai/gpt-4.1)
            cache_path: Path to cache file (default ~/.pipedoc_cache.json)
        """
        # Resolve token
        self.token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub PAT required. Set $GITHUB_TOKEN or pass --token flag."
            )

        # Initialize components
        self.github = GitHub(self.token)
        self.llm = LLM(self.token, model=model)
        self.cache = Cache(cache_path=None if not cache_path else cache_path)

    def analyze(self, run_url: str) -> dict:
        """Run Analyze capability.
        
        Args:
            run_url: GitHub Actions run URL
            
        Returns:
            Result as dict
        """
        cap = Analyze(self.github, self.llm, self.cache, run_url)
        result = cap.execute()
        return {
            "capability": result.capability,
            "findings": result.findings,
            "context": {
                "reduction_pct": result.context.reduction_pct,
            },
            "tokens_used": result.tokens_used,
            "cost_usd": result.cost_usd,
        }

    def review(self, pr_url: str) -> dict:
        """Run Review capability.
        
        Args:
            pr_url: GitHub pull request URL
            
        Returns:
            Result as dict
        """
        cap = Review(self.github, self.llm, self.cache, pr_url)
        result = cap.execute()
        return {
            "capability": result.capability,
            "findings": result.findings,
            "context": {
                "reduction_pct": result.context.reduction_pct,
            },
            "tokens_used": result.tokens_used,
            "cost_usd": result.cost_usd,
        }

    def connectivity_check(self) -> bool:
        """Verify GitHub Models API connectivity.
        
        Returns:
            True if connected, False otherwise
        """
        return self.github.connectivity_check()

    def cache_stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            Cache stats dict
        """
        return self.cache.stats()
