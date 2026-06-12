"""Fingerprint cache for zero-cost repeat failures."""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .filters import normalize_text


class Cache:
    """SHA-256 fingerprint-based cache stored in ~/.pipedoc_cache.json."""

    DEFAULT_CACHE_PATH = Path.home() / ".pipedoc_cache.json"

    def __init__(self, cache_path: Optional[Path] = None):
        """Initialize cache.
        
        Args:
            cache_path: Path to cache JSON file (default ~/.pipedoc_cache.json)
        """
        self.cache_path = cache_path or self.DEFAULT_CACHE_PATH
        self.data = self._load()

    def fingerprint(self, text: str) -> str:
        """Generate SHA-256 fingerprint of normalized text.
        
        Args:
            text: Input text
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        normalized = normalize_text(text)
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, text: str) -> Optional[dict]:
        """Look up cached result by text fingerprint.
        
        Args:
            text: Input text to look up
            
        Returns:
            Cached result dict or None if not found
        """
        fp = self.fingerprint(text)
        return self.data.get(fp)

    def put(self, text: str, result: dict) -> None:
        """Store result in cache.
        
        Args:
            text: Input text
            result: Result dict to cache
        """
        fp = self.fingerprint(text)
        self.data[fp] = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }
        self._save()

    def clear(self) -> None:
        """Clear entire cache."""
        self.data = {}
        self._save()

    def stats(self) -> dict:
        """Get cache statistics.
        
        Returns:
            dict with count, size, etc.
        """
        return {
            "entries": len(self.data),
            "size_bytes": len(json.dumps(self.data)),
            "path": str(self.cache_path),
        }

    def _load(self) -> dict:
        """Load cache from disk."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self) -> None:
        """Save cache to disk."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self.data, f, indent=2)


def fingerprint(text: str) -> str:
    """Standalone fingerprint function.
    
    Args:
        text: Input text
        
    Returns:
        SHA-256 fingerprint
    """
    return Cache().fingerprint(text)
