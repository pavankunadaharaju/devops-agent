# pipedoc — AI-Powered DevOps Agent for CI Diagnostics

**One CLI, one token, your whole CI lifecycle** — diagnose pipeline failures and review pull requests with AI, at near-zero cost.

## Quick Start

### Installation

```bash
pip install -e .
```

### Setup

Export your GitHub Personal Access Token:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Token Permissions Required:**
- `repo` (for accessing repositories)
- `actions:read` (for reading GitHub Actions logs)
- `models:read` (for GitHub Models API access)

### Test Connectivity

```bash
pipedoc check
```

### Diagnose Pipeline Failures

```bash
pipedoc analyze https://github.com/owner/repo/actions/runs/123456
```

### Review Pull Requests

```bash
pipedoc review https://github.com/owner/repo/pull/42 --report
```

---

## Features

### 1. **Pipeline Failure Diagnosis** (`analyze`)

Analyzes failed GitHub Actions runs and provides:
- **Root cause analysis** — what actually went wrong
- **Explanation** — why it failed
- **Suggested fixes** — actionable remediation steps
- **Confidence level** — trust in the diagnosis

**Example Output:**
```
======================================================================
📊 ANALYZE Results
======================================================================

🔍 Findings (1):

  1. [HIGH] Pipeline Failure Diagnosis
     **Root Cause:** Missing Python dependencies in container image
     
     **Explanation:** The Dockerfile does not include requirements.txt 
     
     💡 Fix: Add COPY requirements.txt . before RUN pip install

📉 Context Reduction:
   Raw: 45,230 chars → Sent: 1,240 chars (97.3% reduction)

💰 Cost: $0.0073 USD (487 tokens)
```

### 2. **Pull Request Review** (`review`)

Reviews PRs for:
- **Security vulnerabilities** — potential risks
- **Code bugs** — logic errors
- **CI/K8s misconfigurations** — DevOps issues
- **Performance problems** — inefficiencies

---

## How It Works: The 4-Step Lifecycle

Every capability follows the same pattern:

1. **Gather** — Fetch raw data from GitHub APIs
2. **Distill** — Token-efficient local filtering (MANDATORY, 95%+ reduction)
3. **Reason** — Cache-aware LLM inference (zero-cost on repeat failures)
4. **Act** — Render terminal + HTML output

### Token Efficiency Strategy

```
Input: 50,000 char log
  ↓ (error_window extraction)
1,200 chars (error context)
  ↓ (normalization)
SHA-256 fingerprint
  ↓ (cache check)
→ HIT: $0.00  OR  → MISS: ~2,100 tokens ($0.03)

Typical savings: 95%+ reduction, 100% on cache hits
```

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for:
- **System design** with 12 Mermaid diagrams
- **Data flow** and component interactions
- **Extensibility** patterns for new capabilities
- **Security** and deployment considerations

---

## Commands

### `pipedoc analyze <RUN_URL>`

Diagnose a failed GitHub Actions run.

```bash
pipedoc analyze https://github.com/owner/repo/actions/runs/12345 --report
```

**Options:**
- `--token TEXT` — GitHub PAT (default: `$GITHUB_TOKEN`)
- `--model TEXT` — LLM model (default: `openai/gpt-4.1`)
- `--report` — Generate HTML report

### `pipedoc review <PR_URL>`

Review a pull request.

```bash
pipedoc review https://github.com/owner/repo/pull/99 --report
```

**Options:**
- `--token TEXT` — GitHub PAT (default: `$GITHUB_TOKEN`)
- `--model TEXT` — LLM model (default: `openai/gpt-4.1`)
- `--report` — Generate HTML report

### `pipedoc check`

Verify GitHub Models API connectivity.

```bash
pipedoc check
```

---

## Caching System

pipedoc uses **SHA-256 fingerprint caching** to eliminate duplicate LLM calls.

**Location:** `~/.pipedoc_cache.json`

**Example:**
```bash
# First run: cache MISS → costs $0.03
pipedoc analyze https://github.com/owner/repo/actions/runs/12345

# Same error again: cache HIT → costs $0.00
pipedoc analyze https://github.com/owner/repo/actions/runs/12346
```

---

## Cost Estimation

| Scenario | Tokens | Cost | With Cache Hit |
|----------|--------|------|-----------------|
| Analyze small log | 850 | $0.01 | $0.00 |
| Analyze large log | 2,100 | $0.03 | $0.00 |
| Review small PR | 1,200 | $0.02 | $0.00 |
| Review large PR | 5,000 | $0.07 | $0.00 |

**Naive approach (no filtering):** 50,000+ tokens = $0.75+

**pipedoc savings:** 95%+ reduction, 100% on repeats.

---

## Extensibility: Adding New Capabilities

To add a new capability (e.g., `drift`, `fix`):

```python
from pipedoc.capabilities import Capability, Finding, Result

class NewCapability(Capability):
    @property
    def name(self) -> str:
        return "new-capability"
    
    def gather(self) -> str:
        # Fetch data from GitHub APIs
        pass
    
    def distill(self, raw: str) -> tuple[str, dict]:
        # Token-efficient filtering (MANDATORY)
        pass
    
    def reason(self, distilled: str, metadata: dict) -> tuple[list[Finding], dict]:
        # LLM call + cache
        pass
    
    def act(self, result: Result) -> None:
        # Render output
        pass
```

Register in `pipedoc/capabilities/__init__.py`:
```python
ALL = [Analyze, Review, NewCapability]
```

CLI auto-registers: `pipedoc new-capability`

---

## Roadmap

- [ ] `fix` — Auto-remediation PR generation
- [ ] `drift` — Cluster state vs. Git comparison
- [ ] `postmortem` — Incident report drafting
- [ ] GitLab CI support
- [ ] Team-shared cache (DynamoDB/Redis)
- [ ] `--post` flag for real PR comments
- [ ] Tiered models for cost optimization

---

## Development

### Install editable

```bash
pip install -e .
```

### Install dev tools

```bash
pip install -e ".[dev]"
```

### Format code

```bash
black .
isort .
mypy pipedoc
```

### Run tests

```bash
pytest
```

---

## License

MIT

---

## Configuration

**Environment Variables:**
- `GITHUB_TOKEN` — GitHub Personal Access Token (required)

**Token Permissions:**
- `repo:read` — Access repositories
- `actions:read` — Read GitHub Actions logs
- `models:read` — Access GitHub Models API

---

## Troubleshooting

**Error: "GitHub PAT required"**
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Error: "Failed to connect to GitHub Models API"**
1. Run `pipedoc check` to verify connectivity
2. Check org hasn't disabled GitHub Models
3. Verify token has `models:read` permission
4. Check rate limits

**Error: "Invalid GitHub URL"**
Supported formats:
- Action runs: `https://github.com/owner/repo/actions/runs/12345`
- PRs: `https://github.com/owner/repo/pull/99`

---

## Support & Contributing

- **Issues:** Open an issue on GitHub
- **Discussions:** Start a discussion for feature requests
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details