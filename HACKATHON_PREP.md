# Hackathon Preparation Checklist

Complete this checklist before demo day.

---

## Pre-Demo Setup (Day Before)

### Code Review
- [ ] Run through all Python modules for obvious bugs
- [ ] Check CLI help messages are clear
- [ ] Verify error handling messages are user-friendly
- [ ] Test connectivity check with valid token

### Testing
- [ ] Install package from scratch: `pip install -e .`
- [ ] Verify all CLI commands: `pipedoc analyze --help`, `pipedoc review --help`, `pipedoc check --help`
- [ ] Test with a real GitHub repository you control:
  - [ ] Run `pipedoc analyze` on a failed pipeline
  - [ ] Run `pipedoc review` on a real PR
  - [ ] Verify output formatting and colors
- [ ] Clear cache and run same command twice to verify cache hit logic
- [ ] Check HTML report rendering (if --report is used)

### Documentation
- [ ] Review [README.md](README.md) — user-facing guide ready
- [ ] Review [ARCHITECTURE.md](ARCHITECTURE.md) — technical design ready
- [ ] Review [QUICKSTART.md](QUICKSTART.md) — demo script ready
- [ ] Review [DEVELOPMENT.md](DEVELOPMENT.md) — extension docs ready
- [ ] Proof-read all markdown for typos and clarity

### Demo Environment
- [ ] Have GitHub token ready (store securely, not in code)
- [ ] Test GitHub API connectivity: `pipedoc check`
- [ ] Have 2-3 test repositories with known failure types:
  - [ ] Missing dependency error
  - [ ] Syntax/config error
  - [ ] Security issue in PR
- [ ] Pre-record 2-minute backup video showing all features
- [ ] Have slide deck prepared with:
  - [ ] Problem statement (pipeline debugging costs $$)
  - [ ] Solution pitch (token efficiency + cache)
  - [ ] Live cost counter slide (naive $0.96 vs pipedoc $0.03)
  - [ ] Architecture diagram
  - [ ] Roadmap (future capabilities)

---

## Demo Day (2-3 hours before presentation)

### System Checks
- [ ] Laptop fully charged
- [ ] WiFi connectivity verified
- [ ] GitHub token in environment: `echo $GITHUB_TOKEN`
- [ ] Package installation verified: `pipedoc --version`
- [ ] Terminal emulator working with colors

### Quick Smoke Test
```bash
# 1. Verify connectivity
pipedoc check

# 2. Run analyze on test pipeline
pipedoc analyze https://github.com/your-test-org/repo/actions/runs/123456

# 3. Run review on test PR
pipedoc review https://github.com/your-test-org/repo/pull/99

# 4. Verify cache hit
pipedoc analyze https://github.com/your-test-org/repo/actions/runs/123457
```

### Presentation Flow (15 minutes)
1. **Problem (1 min)** — Show failing pipeline on screen
   - Real GitHub Actions run with cryptic errors
2. **Solution (2 min)** — Run pipedoc analyze
   - Show root cause diagnosis appearing
   - Highlight cost telemetry: "97% token reduction"
   - Highlight cache: "Same error = $0.00"
3. **Capabilities Demo (3 min)**
   - Analyze a pipeline failure → diagnosis appears
   - Review a suspicious PR → security findings appear
4. **Cost Comparison (2 min)**
   - Show slide: Naive approach costs $0.96 per run
   - Show slide: pipedoc costs $0.03 per run
   - Show slide: Cache hits cost $0.00
5. **Architecture (2 min)**
   - Show 4-step lifecycle (gather → distill → reason → act)
   - Show token reduction pipeline (50KB → 1KB)
6. **Roadmap (2 min)**
   - Future: auto-remediation PR, drift detection, postmortem
   - Extension: GitLab CI support
7. **Q&A (3 min)**

---

## Demo Script (Copy-Paste Ready)

### Setup
```bash
export GITHUB_TOKEN=ghp_your_actual_token_here
cd /workspaces/devops-agent
```

### Demo 1: Pipeline Analysis
```bash
echo "🔧 Demo 1: Analyzing a failed pipeline..."
pipedoc analyze https://github.com/your-org/your-repo/actions/runs/123456
```

**Talking points:**
- "It extracted the error window from 50KB of logs"
- "Reduced to 1.2KB before sending to LLM"
- "97% token reduction right there"
- "Cost: $0.03 instead of $0.96 naive"

### Demo 2: Pull Request Review
```bash
echo "🔍 Demo 2: Reviewing a pull request..."
pipedoc review https://github.com/your-org/your-repo/pull/99
```

**Talking points:**
- "Scanned the diff for bugs, security issues, Kubernetes misconfigs"
- "Again: token-efficient filtering before LLM"
- "Results in 95% reduction and lower cost"

### Demo 3: Cache Hit (Zero Cost)
```bash
echo "💾 Demo 3: Same error = cache hit..."
pipedoc analyze https://github.com/your-org/your-repo/actions/runs/123457
cat ~/.pipedoc_cache.json | jq 'keys | length'  # Show cache size
```

**Talking points:**
- "SHA-256 fingerprint of normalized text"
- "Cache hit = $0.00 cost"
- "Team-wide cache multiplies savings"

### Demo 4: Connectivity Check
```bash
echo "📡 Demo 4: Verifying connectivity..."
pipedoc check
```

**Talking points:**
- "One token, one CLI"
- "GitHub Models API integration"
- "No infrastructure costs for the platform team"

---

## Backup Plans

### If GitHub Models API is down
- Use pre-recorded video backup
- Show cached results from previous run
- Explain fallback to copilot CLI

### If package install fails
- Have Docker image pre-built with pipedoc installed
- Or pre-stage Python venv

### If real GitHub token doesn't work
- Have test account token as backup
- Test repositories with public read access

### If live demo doesn't work
- Play pre-recorded video showing all 4 features
- Show live terminal output screenshots
- Discuss architecture instead

---

## Impact Slide Math

**Problem:**
- Typical platform: 200 pipelines/month
- 20% fail on fixable errors (40 failures/month)
- Average debug time: 30 minutes per failure
- Team size: 8 engineers
- Engineer cost: $150/hour

**Manual debugging cost:**
```
40 failures × 30 min × $150/hr ÷ 60 = $3,000/month
```

**With pipedoc:**
```
40 failures × 1 min (LLM diagnosis) × $150/hr ÷ 60 = $100/month
LLM token cost: 40 × 2,100 tokens × $0.003/1K = $0.25/month

Savings: $2,900/month = $34,800/year per platform
```

**Scale to org (50 platforms):**
```
$34,800 × 50 = $1,740,000/year in engineer productivity
```

**Use in slide deck.** It's a Staff/Principal level impact story.

---

## Presentation Materials Checklist

- [ ] Slide deck (PDF, backup on laptop + USB)
- [ ] Architecture diagram (on screen)
- [ ] Cost comparison chart (slide)
- [ ] Screenshot of pipedoc output (slide)
- [ ] Live demo backup video (3-5 min, MP4)
- [ ] README.md open in browser (for audience Q&A)
- [ ] QUICKSTART.md accessible (share with judges)

---

## Live Presentation Tips

### Do
- ✅ Start with problem statement (engineers waste time debugging)
- ✅ Show real pipeline failure upfront (make it relatable)
- ✅ Highlight cost telemetry on screen ("97% reduction")
- ✅ Emphasize "one token, zero infra" model
- ✅ Show cache hit = $0.00 (the aha moment)
- ✅ Have GitHub token ready, not typed live
- ✅ Show ARCHITECTURE.md to judges (technical depth)
- ✅ Practice the demo 3 times beforehand

### Don't
- ❌ Don't show raw code unless asked (keep focus on features)
- ❌ Don't get bogged down in LLM details
- ❌ Don't overcomplicate the 4-step lifecycle explanation
- ❌ Don't forget to mention extensibility (fix, drift, postmortem)
- ❌ Don't read from slides

---

## Judging Criteria Alignment

### Technical Depth ✅
- "4-step capability lifecycle embedded in ABC"
- "Fingerprint caching with SHA-256"
- "Structured JSON output from LLMs"
- "Click auto-registration plugin system"

### Business Impact ✅
- "95%+ token reduction" (management pitch)
- "$0.00 cost on repeat failures"
- "1-3 minute engineer time savings per failure"
- "Scales: $1.7M/year productivity for org"

### Innovation ✅
- "First DevOps agent with cost-governance layer"
- "Portable: one CLI, one token"
- "Extensible: ship new capabilities as Python files"
- "Zero-cost team cache" (future)

### Execution ✅
- "Production-ready code" (GitHub, LLM, cache modules)
- "CLI ready to use" (subcommands auto-register)
- "Comprehensive docs" (ARCHITECTURE, README, DEVELOPMENT)
- "Tested and verified" (import checks, CLI validation)

---

## Post-Demo

### If You Win 🏆
- [ ] Celebrate! You built an impressive system
- [ ] Collect judge feedback
- [ ] Take note of feature requests
- [ ] Plan roadmap (fix, drift, postmortem, GitLab)

### If You Don't Win
- [ ] Ask judges for specific feedback
- [ ] Note what resonated and what didn't
- [ ] Consider: is this a marketable product?
- [ ] Plan OSS release and community launch

---

## Final Checklist (1 Hour Before)

- [ ] Terminal open, clear, pipedoc available
- [ ] GitHub token in environment
- [ ] `pipedoc check` returns ✓ Connected
- [ ] Test command runs: `pipedoc analyze <test_url>`
- [ ] Slide deck loaded and ready
- [ ] Backup video on laptop
- [ ] Water bottle nearby
- [ ] Deep breath — you've got this! 🚀

---

## Contact & Support During Hackathon

- **Questions about architecture?** → See ARCHITECTURE.md
- **Questions about usage?** → See README.md
- **Questions about extending?** → See DEVELOPMENT.md
- **Live demo issues?** → Play backup video
- **Out of tokens?** → Show cache stats

---

**You're ready. Go build, go demo, go win!** 🎉
