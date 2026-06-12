"""Capability plugins for pipedoc."""

from .base import Capability, Confidence, Context, Finding, Result, Severity
from .analyze import Analyze
from .review import Review

# Registry of all available capabilities
ALL = [Analyze, Review]

__all__ = [
    "Capability",
    "Context",
    "Finding",
    "Result",
    "Severity",
    "Confidence",
    "Analyze",
    "Review",
    "ALL",
]
