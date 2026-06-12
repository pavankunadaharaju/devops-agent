"""LLM interface for GitHub Models API."""

import json
import re
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass
class TokenUsage:
    """Token usage statistics."""

    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens


class LLM:
    """GitHub Models API client for LLM inference."""

    # Pricing per 1K tokens (placeholders - tune to actual model)
    PRICE_PER_1K_IN = 0.0015  # $1.50 per 1M input tokens
    PRICE_PER_1K_OUT = 0.006  # $6.00 per 1M output tokens

    ENDPOINT = "https://models.github.ai/inference/chat/completions"
    DEFAULT_MODEL = "openai/gpt-4.1"
    DEFAULT_TEMPERATURE = 0.2
    DEFAULT_MAX_TOKENS = 800

    def __init__(self, token: str, model: Optional[str] = None):
        """Initialize LLM client.
        
        Args:
            token: GitHub personal access token
            model: Model name (default: openai/gpt-4.1)
        """
        self.token = token
        self.model = model or self.DEFAULT_MODEL
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.total_tokens_used = 0
        self.total_cost = 0.0

    def call(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> tuple[str, TokenUsage]:
        """Make an inference call to GitHub Models API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (default 0.2)
            max_tokens: Max output tokens (default 800)
            
        Returns:
            Tuple of (response_text, TokenUsage)
        """
        temperature = temperature or self.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = TokenUsage(
            input_tokens=data["usage"]["prompt_tokens"],
            output_tokens=data["usage"]["completion_tokens"],
        )

        # Track aggregate usage
        self.total_tokens_used += usage.total_tokens
        self.total_cost += self._calculate_cost(usage)

        return content, usage

    def parse_json(self, text: str) -> dict:
        """Parse JSON from LLM response, stripping markdown fences if present.
        
        Args:
            text: LLM response text
            
        Returns:
            Parsed JSON dict
        """
        # Strip markdown ```json``` fences
        text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        text = text.strip()
        return json.loads(text)

    def _calculate_cost(self, usage: TokenUsage) -> float:
        """Calculate USD cost for token usage.
        
        Args:
            usage: TokenUsage object
            
        Returns:
            Cost in USD
        """
        input_cost = (usage.input_tokens / 1000) * self.PRICE_PER_1K_IN
        output_cost = (usage.output_tokens / 1000) * self.PRICE_PER_1K_OUT
        return input_cost + output_cost

    def get_cost(self) -> float:
        """Get total accumulated cost so far.
        
        Returns:
            Total cost in USD
        """
        return self.total_cost

    @property
    def endpoint(self) -> str:
        """Get the API endpoint."""
        return self.ENDPOINT
