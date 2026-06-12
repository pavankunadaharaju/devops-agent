"""Base capability system for pipedoc."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Severity(str, Enum):
    """Severity levels for findings."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "med"
    HIGH = "high"


class Confidence(str, Enum):
    """Confidence levels for findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Context:
    """Represents raw + distilled state for a capability."""

    raw: str
    distilled: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def reduction_pct(self) -> float:
        """Calculate reduction percentage."""
        if len(self.raw) == 0:
            return 0.0
        return ((len(self.raw) - len(self.distilled)) / len(self.raw)) * 100


@dataclass
class Finding:
    """Single diagnostic result from a capability."""

    title: str
    detail: str
    severity: Severity
    location: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: Confidence = Confidence.MEDIUM
    cached: bool = False


@dataclass
class Result:
    """Complete capability execution result."""

    capability: str
    findings: list[Finding]
    context: Context
    tokens_used: int
    cost_usd: float


class Capability(ABC):
    """Abstract base class for all capabilities.
    
    Every capability must implement:
    1. gather() - fetch raw data from GitHub APIs
    2. distill() - token-efficient reduction (MANDATORY)
    3. reason() - cache-aware LLM call(s), structured JSON output
    4. act() - terminal output / HTML report
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Capability name (used as CLI subcommand)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what this capability does."""
        pass

    @abstractmethod
    def gather(self) -> str:
        """Fetch raw data from GitHub APIs.
        
        Returns:
            Raw context string
        """
        pass

    @abstractmethod
    def distill(self, raw: str) -> tuple[str, dict]:
        """Token-efficient reduction (MANDATORY).
        
        Args:
            raw: Raw data from gather()
            
        Returns:
            Tuple of (distilled_text, metadata_dict)
        """
        pass

    @abstractmethod
    def reason(self, distilled: str, metadata: dict) -> tuple[list[Finding], dict]:
        """Cache-aware LLM call(s) with structured JSON output.
        
        Args:
            distilled: Distilled text from distill()
            metadata: Metadata from distill()
            
        Returns:
            Tuple of (findings_list, usage_dict with tokens_used and cost)
        """
        pass

    @abstractmethod
    def act(self, result: Result) -> None:
        """Render output to terminal / HTML report.
        
        Args:
            result: Complete Result object
        """
        pass

    def execute(self) -> Result:
        """Execute full 4-step lifecycle.
        
        Returns:
            Result object with findings and telemetry
        """
        # Step 1: Gather
        raw = self.gather()

        # Step 2: Distill
        distilled, metadata = self.distill(raw)

        # Step 3: Reason
        findings, usage = self.reason(distilled, metadata)

        # Step 4: Act
        context = Context(raw=raw, distilled=distilled, metadata=metadata)
        result = Result(
            capability=self.name,
            findings=findings,
            context=context,
            tokens_used=usage.get("tokens_used", 0),
            cost_usd=usage.get("cost_usd", 0.0),
        )
        self.act(result)

        return result
