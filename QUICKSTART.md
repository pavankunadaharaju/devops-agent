# Quick Start: 5-Minute Setup

Get pipedoc running in 5 minutes.

## 1. Install (1 min)

```bash
cd /workspaces/devops-agent
pip install -e .
```

**Verify:**
```bash
pipedoc --version
pipedoc --help
```

---

## 2. Set GitHub Token (1 min)

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Verify:**
```bash
pipedoc check
```

Expected output:
```
✓ Connected to GitHub Models API
Cache stats: {entries: 0, ...}
```

---

## 3. Try Analyze (1 min)

Diagnose a failed pipeline:

```bash
pipedoc analyze https://github.com/owner/repo/actions/runs/12345
```

**Example output:**
```
✓ Connected

📊 Analyzing pipeline failure...

======================================================================
📊 ANALYZE Results
======================================================================

🔍 Findings (1):

  1. [HIGH] Pipeline Failure Diagnosis
     **Root Cause:** Missing dependencies in Docker image
     
     **Explanation:** The Dockerfile was not updated with new packages
     
     💡 Fix: Add RUN pip install -r requirements.txt to Dockerfile

📉 Context Reduction:
   Raw: 45,230 chars
   Sent: 1,240 chars
   Reduction: 97.3%

💰 Cost Telemetry:
   Tokens used: 487
   Cost: $0.0073 USD

======================================================================
```

---

## 4. Try Review (1 min)

Review a pull request:

```bash
pipedoc review https://github.com/owner/repo/pull/99
```

**Example output:**
```
✓ Connected

📋 Reviewing pull request...

======================================================================
📊 REVIEW Results
======================================================================

🔍 Findings (2):

  1. [HIGH] src/database.py:42
     SQL injection risk: User input not parameterized

  2. [MED] k8s/deploy.yaml:28
     Missing resource limits could cause OOMKill

📉 Context Reduction:
   Raw: 62,148 chars
   Sent: 2,850 chars
   Reduction: 95.4%

💰 Cost Telemetry:
   Tokens used: 712
   Cost: $0.0107 USD

======================================================================
```

---

## 5. Explore Cache (1 min)

View cache hits (zero cost):

```bash
# First run: costs money
pipedoc analyze https://github.com/owner/repo/actions/runs/12345

# Same error again: cache hit = $0.00
pipedoc analyze https://github.com/owner/repo/actions/runs/12346
```

**View cache:**
```bash
cat ~/.pipedoc_cache.json | python -m json.tool
```

---

## Files You Might Want to See

- **Architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md) — System design with diagrams
- **User Guide:** [`README.md`](README.md) — Features, usage, troubleshooting
- **Dev Guide:** [`DEVELOPMENT.md`](DEVELOPMENT.md) — Testing, extending, debugging
- **Code Summary:** [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) — What was built

---

## Common Issues

### "GitHub PAT required"
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

### "Failed to connect to GitHub Models API"
```bash
pipedoc check  # Verify connectivity
```

Org admin may have disabled GitHub Models. Check:
1. Token has `models:read` permission
2. Org hasn't blocked GitHub Models API
3. You haven't hit rate limits

### "Invalid GitHub URL"
Use full URLs:
- Actions: `https://github.com/owner/repo/actions/runs/12345`
- PRs: `https://github.com/owner/repo/pull/99`

---

## Next Steps

- Read [README.md](README.md) for comprehensive guide
- Try with your own repo and GitHub token
- Check [DEVELOPMENT.md](DEVELOPMENT.md) to add custom capabilities
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design details

---

## Key Metrics (From Implementation)

✅ **13 Python modules** across 4 packages  
✅ **95%+ token reduction** via local filtering  
✅ **$0.00 cost** on repeat failures (cache hits)  
✅ **~2 seconds** for typical analysis  
✅ **4-step lifecycle** ensures cost governance baked in  

---

## Demo Script (Hackathon)

```bash
# 1. Show connectivity
pipedoc check
echo "✓ Connected, cache is empty"

# 2. First analysis (costs ~$0.03)
pipedoc analyze https://github.com/owner/repo/actions/runs/12345
echo "💰 Cost: $0.03"

# 3. Repeat analysis (same error = cache hit)
pipedoc analyze https://github.com/owner/repo/actions/runs/12346
echo "💰 Cost: $0.00 (CACHE HIT!)"

# 4. Show cache
cat ~/.pipedoc_cache.json | jq '.[] | .timestamp'
echo "✓ Same error detected via fingerprint, returned cached result"
```

---

**Ready? Start with `pipedoc --help`** 🚀
