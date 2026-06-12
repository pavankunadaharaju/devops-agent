"""Token-efficient text filtering and normalization."""

import re
from typing import Optional

# Files/patterns to skip in diff analysis
SKIP_FILES = re.compile(
    r"\.(lock|json|yaml|yml|txt|md|html|css|js)$"
    r"|package-lock\.json|yarn\.lock|poetry\.lock|Gemfile\.lock"
    r"|\.git/|node_modules/|\.vendor/|dist/|build/|__pycache__/"
    r"|\.egg-info/",
    re.IGNORECASE,
)

# Hard cap on characters to send to LLM
MAX_CHARS = 12000

# Patterns to detect error windows
ERROR_PATTERNS = re.compile(
    r"(?i)(error|failed|fatal|traceback|exception|exit\s*code|##\[error\])",
    re.IGNORECASE,
)


def error_window(text: str, context_lines: int = 8, keep_last: int = 40) -> str:
    """Extract error context windows from raw text with local filtering.
    
    Strategy:
    - Find lines matching ERROR_PATTERNS
    - Keep ±context_lines around each match
    - Always keep last keep_last lines (often the root cause)
    - Cap output at MAX_CHARS
    
    Args:
        text: Raw input text (log, error output, etc.)
        context_lines: Lines of context before/after match
        keep_last: Always keep this many lines from end
        
    Returns:
        Filtered text with error windows
    """
    lines = text.split("\n")

    if len(lines) <= keep_last:
        return text

    # Find error line indices
    error_indices = set()
    for i, line in enumerate(lines):
        if ERROR_PATTERNS.search(line):
            # Add context window around this line
            for j in range(max(0, i - context_lines), min(len(lines), i + context_lines + 1)):
                error_indices.add(j)

    # Always include last keep_last lines
    for i in range(max(0, len(lines) - keep_last), len(lines)):
        error_indices.add(i)

    # Build output preserving order
    if not error_indices:
        # No errors found, keep last keep_last lines
        output_lines = lines[-keep_last:]
    else:
        output_lines = [lines[i] for i in sorted(error_indices)]

    result = "\n".join(output_lines)

    # Cap at MAX_CHARS
    if len(result) > MAX_CHARS:
        result = result[-MAX_CHARS:]

    return result


def diff_per_file(diff_text: str) -> list[dict]:
    """Parse unified diff and chunk per file, skipping vendored/generated files.
    
    Strategy:
    - Split by `diff --git` markers (unified diff format)
    - Skip files matching SKIP_FILES
    - Per-file diffs are capped individually
    - Return list of file diffs with metadata
    
    Args:
        diff_text: Unified diff text
        
    Returns:
        List of dicts: {file, diff, size}
    """
    result = []
    current_file = None
    current_diff = []
    max_per_file = 5000  # Cap per-file diff size

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            # Save previous file if exists
            if current_file and current_diff:
                diff_content = "\n".join(current_diff)
                if len(diff_content) > max_per_file:
                    diff_content = diff_content[:max_per_file] + "\n... (truncated)"
                result.append({"file": current_file, "diff": diff_content, "size": len(diff_content)})

            # Parse new file
            match = re.search(r"a/(.*?)\s+b/(.*?)$", line)
            if match:
                current_file = match.group(2)
                current_diff = [line]
            else:
                current_file = None
                current_diff = []
        else:
            if current_file:
                current_diff.append(line)

    # Save last file
    if current_file and current_diff and not SKIP_FILES.search(current_file):
        diff_content = "\n".join(current_diff)
        if len(diff_content) > max_per_file:
            diff_content = diff_content[:max_per_file] + "\n... (truncated)"
        result.append({"file": current_file, "diff": diff_content, "size": len(diff_content)})

    # Filter out skipped files
    result = [r for r in result if not SKIP_FILES.search(r["file"])]

    return result


def normalize_text(text: str) -> str:
    """Normalize text to reduce variance in hashing/caching.
    
    Strategy:
    - Replace URLs with <hash>
    - Replace line numbers with line <n>
    - Replace tmp paths with <tmp>
    - Collapse multiple spaces
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    # URLs → <hash>
    text = re.sub(r"https?://\S+", "<hash>", text)

    # Hex strings → <hash>
    text = re.sub(r"\b[a-f0-9]{40,}\b", "<hash>", text)

    # Line numbers: "line 123" → "line <n>"
    text = re.sub(r"line\s+\d+", "line <n>", text, flags=re.IGNORECASE)

    # Temp paths
    text = re.sub(r"(/tmp/|C:\\Temp\\)\S*", "<tmp>", text)

    # Timestamps (rough)
    text = re.sub(r"\d{4}-\d{2}-\d{2}T?\d{2}:\d{2}:\d{2}", "<timestamp>", text)

    # Multiple spaces
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def calculate_reduction(original: str, filtered: str) -> float:
    """Calculate reduction percentage.
    
    Args:
        original: Original text
        filtered: Filtered text
        
    Returns:
        Percentage reduction (0-100)
    """
    if len(original) == 0:
        return 0.0
    return ((len(original) - len(filtered)) / len(original)) * 100
