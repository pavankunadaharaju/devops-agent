# Development Guide

This guide covers local development, testing, and contributing to pipedoc.

## Setup

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token with `repo`, `actions:read`, `models:read` permissions

### Clone & Install

```bash
git clone https://github.com/pavankunadaharaju/devops-agent.git
cd devops-agent

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
pipedoc --version
pipedoc --help
```

---

## Local Development

### Environment Setup

```bash
# Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Verify connectivity
pipedoc check
```

### Code Organization

```
pipedoc/
├── core/                 # Core utilities
│   ├── github.py        # GitHub API client
│   ├── llm.py           # LLM interface
│   ├── filters.py       # Token-efficient filters
│   └── cache.py         # Fingerprint cache
├── capabilities/        # Capability plugins
│   ├── base.py          # ABC and data models
│   ├── analyze.py       # Pipeline diagnosis
│   ├── review.py        # PR review
│   └── __init__.py      # Registry
├── agent.py             # Orchestrator
├── cli.py               # Click CLI
└── render.py            # Output rendering
```

---

## Testing

### Run Test Suite

```bash
pytest
```

### Run Specific Test

```bash
pytest tests/test_core/test_github.py -v
```

### Coverage Report

```bash
pytest --cov=pipedoc --cov-report=html
```

### Test Fixtures

Create test GitHub URLs:
- Action run: `https://github.com/owner/repo/actions/runs/12345`
- PR: `https://github.com/owner/repo/pull/99`

### Mock GitHub API

For tests, mock the GitHub client:

```python
from unittest.mock import Mock, patch
from pipedoc.core import GitHub

def test_parse_url():
    github = GitHub("fake_token")
    
    # Test action run URL
    result = github.parse_url(
        "https://github.com/owner/repo/actions/runs/12345"
    )
    assert result["owner"] == "owner"
    assert result["repo"] == "repo"
    assert result["run_id"] == 12345
    
    # Test PR URL
    result = github.parse_url(
        "https://github.com/owner/repo/pull/99"
    )
    assert result["pr_number"] == 99
```

### Mock LLM API

```python
from unittest.mock import Mock, patch
from pipedoc.core import LLM, TokenUsage

def test_llm_call():
    llm = LLM("fake_token")
    
    with patch('requests.post') as mock_post:
        # Mock GitHub Models response
        mock_post.return_value.json.return_value = {
            "choices": [{
                "message": {"content": '{"root_cause": "Missing dependency"}'}
            }],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50}
        }
        
        response, usage = llm.call([{"role": "user", "content": "test"}])
        assert "root_cause" in response
        assert usage.total_tokens == 150
```

---

## Code Style

### Format Code

```bash
# Auto-format with Black
black pipedoc tests

# Sort imports
isort pipedoc tests

# Check style
flake8 pipedoc tests

# Type checking
mypy pipedoc
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

---

## Adding New Capabilities

### Example: New Capability `drift`

1. **Create file:** `pipedoc/capabilities/drift.py`

```python
from pipedoc.capabilities import Capability, Finding, Result, Severity, Confidence
from pipedoc.core import GitHub, LLM, Cache

class Drift(Capability):
    """Detect configuration drift between cluster and Git."""
    
    def __init__(self, github: GitHub, llm: LLM, cache: Cache, cluster_url: str):
        self.github = github
        self.llm = llm
        self.cache = cache
        self.cluster_url = cluster_url
    
    @property
    def name(self) -> str:
        return "drift"
    
    @property
    def description(self) -> str:
        return "Compare live cluster state vs. Git configuration"
    
    def gather(self) -> str:
        # Fetch live cluster state (e.g., via kubectl)
        # Fetch Git manifests from repo
        pass
    
    def distill(self, raw: str) -> tuple[str, dict]:
        # Filter and normalize diffs
        pass
    
    def reason(self, distilled: str, metadata: dict) -> tuple[list[Finding], dict]:
        # LLM analyzes drift
        pass
    
    def act(self, result: Result) -> None:
        # Render findings
        pass
```

2. **Register** in `pipedoc/capabilities/__init__.py`:

```python
from .drift import Drift
ALL = [Analyze, Review, Drift]
```

3. **Test:**

```python
def test_drift_capability():
    drift = Drift(github, llm, cache, "https://cluster.example.com")
    result = drift.execute()
    assert result.capability == "drift"
    assert len(result.findings) > 0
```

4. **CLI auto-registers:**

```bash
pipedoc drift --help
```

---

## Performance Profiling

### Profile Memory Usage

```python
from pympler import tracker

tr = tracker.SummaryTracker()

# Run capability
result = agent.analyze(run_url)

tr.print_diff()
```

### Profile Execution Time

```python
import time

start = time.time()
result = agent.analyze(run_url)
elapsed = time.time() - start

print(f"Execution time: {elapsed:.2f}s")
print(f"Tokens: {result['tokens_used']}")
print(f"Cost: ${result['cost_usd']:.6f}")
```

---

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pipedoc")
logger.setLevel(logging.DEBUG)
```

### Debug CLI Commands

```bash
# Run with Python debugger
python -m pdb -m pipedoc.cli analyze https://github.com/owner/repo/actions/runs/12345

# Or use ipdb
ipdb -m pipedoc.cli analyze https://github.com/owner/repo/actions/runs/12345
```

### Inspect Cache

```bash
cat ~/.pipedoc_cache.json | python -m json.tool
```

---

## Release Process

### Version Bumping

1. Update version in `pyproject.toml`
2. Update `pipedoc/__init__.py` `__version__`
3. Tag release: `git tag v0.1.0`
4. Push tags: `git push --tags`

### Build Distribution

```bash
# Clean previous builds
rm -rf dist build *.egg-info

# Build wheel
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

---

## Documentation

### Update Architecture Docs

See [ARCHITECTURE.md](../ARCHITECTURE.md) for system design.

### Add Docstrings

All public functions should have docstrings:

```python
def my_function(arg: str) -> dict:
    """Short description.
    
    Longer description if needed.
    
    Args:
        arg: Argument description
        
    Returns:
        Return value description
        
    Raises:
        ValueError: When something is wrong
    """
    pass
```

### Update README

Update [README.md](../README.md) with:
- New capabilities
- Usage examples
- Configuration changes

---

## Continuous Integration

### GitHub Actions Workflow

(Create `.github/workflows/test.yml`)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: black --check pipedoc tests
      - run: isort --check pipedoc tests
      - run: mypy pipedoc
      - run: pytest
```

---

## Common Tasks

### Add New Filter

```python
# In pipedoc/core/filters.py
def new_filter(text: str) -> str:
    """Filter description."""
    # Implementation
    return filtered_text

# In pipedoc/core/__init__.py
from .filters import new_filter
__all__ = [..., "new_filter"]
```

### Add New LLM Model

```python
# In pipedoc/core/llm.py
LLM_MODELS = {
    "openai/gpt-4.1": {
        "price_per_1k_in": 0.0015,
        "price_per_1k_out": 0.006,
    },
    "openai/gpt-4-turbo": {
        "price_per_1k_in": 0.01,
        "price_per_1k_out": 0.03,
    },
}
```

### Add CLI Command

```python
# In pipedoc/cli.py
@main.command()
@click.argument("url")
@click.option("--token", envvar="GITHUB_TOKEN")
def new_command(url: str, token: Optional[str]) -> None:
    """Command description."""
    agent = Agent(github_token=token)
    # Implementation
```

---

## Troubleshooting Development

### "ModuleNotFoundError: No module named 'pipedoc'"

```bash
pip install -e .
```

### "GitHub Models API connection failed"

```bash
export GITHUB_TOKEN=ghp_your_token_here
pipedoc check
```

### "Tests fail with 'No such file'"

Ensure you're running tests from repo root:

```bash
cd /workspaces/devops-agent
pytest
```

### "LLM response parse error"

Check LLM response format:

```python
# In tests, mock response properly
mock_post.return_value.json.return_value = {
    "choices": [{
        "message": {"content": '{"key": "value"}'}  # Valid JSON
    }],
    "usage": {"prompt_tokens": 100, "completion_tokens": 50}
}
```

---

## Resources

- **Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md)
- **README:** [README.md](../README.md)
- **Click Docs:** https://click.palletsprojects.com/
- **Pydantic Docs:** https://docs.pydantic.dev/
- **GitHub API Docs:** https://docs.github.com/en/rest
- **GitHub Models API:** https://models.github.ai/

---

## Support

- **Questions?** Open a discussion
- **Found a bug?** Open an issue
- **Have an idea?** Open a feature request
