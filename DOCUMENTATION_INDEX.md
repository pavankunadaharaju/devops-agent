# Documentation Index

**Quick navigation for pipedoc project documentation.**

---

## 📋 Documentation Files

### For Users
| File | Purpose | Read If... |
|------|---------|-----------|
| [README.md](README.md) | User guide & reference | You want to use pipedoc |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute setup guide | You want to get started fast |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current project status | You want to know what's done |

### For Developers
| File | Purpose | Read If... |
|------|---------|-----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & diagrams | You want to understand how it works |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Dev environment & testing | You want to extend or modify code |

### For Demo Day
| File | Purpose | Read If... |
|------|---------|-----------|
| [HACKATHON_PREP.md](HACKATHON_PREP.md) | Demo preparation guide | You're preparing for hackathon demo |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | What was built | You want a quick summary of deliverables |

---

## 🎯 Quick Links by Task

### I Want To...

#### **Use pipedoc**
1. Read [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. Follow the setup: `pip install -e .`, then `pipedoc check`
3. Try: `pipedoc analyze <run_url>` or `pipedoc review <pr_url>`
4. See [README.md](README.md) for detailed usage

#### **Understand the architecture**
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) — 12 Mermaid diagrams
2. Focus on: System Overview, 4-Step Lifecycle, Token Efficiency
3. Then read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

#### **Add a new capability**
1. Read [DEVELOPMENT.md](DEVELOPMENT.md) — "Adding New Capabilities" section
2. Create `pipedoc/capabilities/my_capability.py`
3. Implement 4-step lifecycle (gather → distill → reason → act)
4. Register in `pipedoc/capabilities/__init__.py`

#### **Debug an issue**
1. Check [README.md](README.md) — "Troubleshooting" section
2. Read [DEVELOPMENT.md](DEVELOPMENT.md) — "Debugging" section
3. Check cache: `cat ~/.pipedoc_cache.json`

#### **Prepare for demo**
1. Read [HACKATHON_PREP.md](HACKATHON_PREP.md) — complete guide
2. Follow pre-demo checklist
3. Use provided demo script
4. Reference [PROJECT_STATUS.md](PROJECT_STATUS.md) for metrics

#### **Understand project status**
1. Read [PROJECT_STATUS.md](PROJECT_STATUS.md) — what's done
2. Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — deliverables
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical depth

---

## 📚 Reading Guide by Role

### For Product Managers
1. Start: [README.md](README.md) — Features section
2. Then: [PROJECT_STATUS.md](PROJECT_STATUS.md) — Cost Analysis
3. Finally: [HACKATHON_PREP.md](HACKATHON_PREP.md) — Impact slide math

### For Engineers
1. Start: [ARCHITECTURE.md](ARCHITECTURE.md) — System Overview
2. Then: [DEVELOPMENT.md](DEVELOPMENT.md) — Setup & Testing
3. Ref: [README.md](README.md) — Troubleshooting

### For DevOps
1. Start: [QUICKSTART.md](QUICKSTART.md) — 5-minute setup
2. Then: [README.md](README.md) — Usage examples
3. Ref: [HACKATHON_PREP.md](HACKATHON_PREP.md) — Demo script

### For Hackathon Judges
1. Start: [PROJECT_STATUS.md](PROJECT_STATUS.md) — Overview
2. Then: [ARCHITECTURE.md](ARCHITECTURE.md) — System design (12 diagrams)
3. Then: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — Deliverables
4. Finally: [HACKATHON_PREP.md](HACKATHON_PREP.md) — Impact & roadmap

---

## 🔍 Key Concepts by Document

| Concept | Where to Learn |
|---------|---------|
| **Token Efficiency** | [ARCHITECTURE.md](ARCHITECTURE.md) — Token-Efficiency Strategy section |
| **4-Step Lifecycle** | [ARCHITECTURE.md](ARCHITECTURE.md) — 4-Step Capability Lifecycle |
| **Fingerprint Cache** | [ARCHITECTURE.md](ARCHITECTURE.md) — Fingerprint Cache diagram |
| **CLI Auto-Registration** | [ARCHITECTURE.md](ARCHITECTURE.md) — CLI Structure diagram |
| **Extension Points** | [DEVELOPMENT.md](DEVELOPMENT.md) — Adding New Capabilities |
| **Cost Calculation** | [PROJECT_STATUS.md](PROJECT_STATUS.md) — Cost Analysis |
| **Demo Flow** | [HACKATHON_PREP.md](HACKATHON_PREP.md) — Demo Script |
| **Troubleshooting** | [README.md](README.md) — Troubleshooting section |

---

## 📖 Document Summaries

### README.md (User Guide)
- **Length:** 200 lines
- **Purpose:** Complete user guide
- **Contains:** Quick start, features, usage, troubleshooting, cost estimation
- **Best for:** Anyone learning to use pipedoc

### ARCHITECTURE.md (System Design)
- **Length:** 500 lines
- **Purpose:** Technical deep-dive with diagrams
- **Contains:** 12 Mermaid diagrams, system overview, component interactions, data flows
- **Best for:** Engineers, architects, judges

### DEVELOPMENT.md (Developer Guide)
- **Length:** 300 lines
- **Purpose:** Development environment and extension guide
- **Contains:** Setup, testing, code style, adding capabilities, debugging, CI/CD
- **Best for:** Contributors, maintainers

### QUICKSTART.md (5-Minute Guide)
- **Length:** 200 lines
- **Purpose:** Fast onboarding
- **Contains:** Installation, setup, 3 quick commands, cache demo
- **Best for:** Users who want immediate results

### HACKATHON_PREP.md (Demo Guide)
- **Length:** 250 lines
- **Purpose:** Complete preparation for demo day
- **Contains:** Checklists, demo script, impact math, backup plans, tips
- **Best for:** Anyone presenting the project

### IMPLEMENTATION_SUMMARY.md (What Was Built)
- **Length:** 150 lines
- **Purpose:** Summary of deliverables
- **Contains:** Files created, features, verification, next steps
- **Best for:** Quick overview of project scope

### PROJECT_STATUS.md (Complete Status)
- **Length:** 400 lines
- **Purpose:** Comprehensive project status
- **Contains:** What's done, verification, performance profile, metrics, roadmap
- **Best for:** Project stakeholders, judges

---

## 🚀 Getting Started

### 1. New to the project? (5 min)
```
Read: QUICKSTART.md
Do: pip install -e . && pipedoc check
```

### 2. Want to use it? (10 min)
```
Read: README.md
Try: pipedoc analyze <your_run_url>
```

### 3. Want to understand it? (30 min)
```
Read: ARCHITECTURE.md (with diagrams)
Understand: 4-step lifecycle, token efficiency, caching
```

### 4. Want to extend it? (1 hour)
```
Read: DEVELOPMENT.md - Adding New Capabilities
Create: pipedoc/capabilities/my_cap.py
Register: In __init__.py
```

### 5. Presenting it? (2 hours)
```
Read: HACKATHON_PREP.md - complete checklist
Practice: Demo script 3 times
Review: Impact math and business case
```

---

## 📞 FAQ - Which Document?

**Q: How do I install pipedoc?**
A: [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md) — Installation section

**Q: What's the cost per run?**
A: [PROJECT_STATUS.md](PROJECT_STATUS.md) — Cost Analysis section

**Q: How do I add a new capability?**
A: [DEVELOPMENT.md](DEVELOPMENT.md) — Adding New Capabilities section

**Q: What was actually built?**
A: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — Files Created section

**Q: How does the caching work?**
A: [ARCHITECTURE.md](ARCHITECTURE.md) — Fingerprint Cache diagram

**Q: Can I use a different LLM?**
A: [ARCHITECTURE.md](ARCHITECTURE.md) — Component Architecture (LLM Module)

**Q: What's the demo script?**
A: [HACKATHON_PREP.md](HACKATHON_PREP.md) — Demo Script section

**Q: How long does analysis take?**
A: [PROJECT_STATUS.md](PROJECT_STATUS.md) — Performance Profile table

**Q: What's the business impact?**
A: [HACKATHON_PREP.md](HACKATHON_PREP.md) — Impact Slide Math section

**Q: Where's the code?**
A: `pipedoc/` directory (or read [ARCHITECTURE.md](ARCHITECTURE.md) for overview)

---

## 📊 Document Dependency Graph

```
PROJECT_STATUS.md (Start here if new)
    ↓
QUICKSTART.md (Get running)
    ↓
README.md (Learn usage)
    ↓
ARCHITECTURE.md (Understand design)
    ↓
DEVELOPMENT.md (Extend)

HACKATHON_PREP.md (For demo)
    ↓
IMPLEMENTATION_SUMMARY.md (What was built)
```

---

## ✅ Document Checklist

Before demo:
- [ ] Read PROJECT_STATUS.md — understand what's done
- [ ] Read QUICKSTART.md — verify you can run it
- [ ] Read ARCHITECTURE.md — understand the design
- [ ] Read HACKATHON_PREP.md — prepare for demo

---

## 🎓 Learning Path

### Beginner (Want to use)
1. QUICKSTART.md (5 min)
2. README.md (15 min)
3. Done! Start using pipedoc

### Intermediate (Want to understand)
1. README.md (15 min)
2. ARCHITECTURE.md (30 min)
3. IMPLEMENTATION_SUMMARY.md (10 min)

### Advanced (Want to extend)
1. ARCHITECTURE.md (30 min)
2. DEVELOPMENT.md (1 hour)
3. Create a custom capability

### Expert (Want to present/judge)
1. PROJECT_STATUS.md (15 min)
2. ARCHITECTURE.md (30 min)
3. HACKATHON_PREP.md (20 min)
4. Source code review (30 min)

---

## 📋 Quick Reference

### CLI Commands
```bash
pipedoc analyze <run_url>      # Diagnose pipeline failure
pipedoc review <pr_url>         # Review pull request
pipedoc check                   # Verify connectivity
```

### Setup
```bash
pip install -e .                # Install
export GITHUB_TOKEN=ghp_xxx     # Set token
pipedoc check                   # Verify
```

### Key Files
- `pipedoc/core/github.py` — GitHub API client
- `pipedoc/core/llm.py` — LLM interface
- `pipedoc/core/filters.py` — Token reduction
- `pipedoc/core/cache.py` — Fingerprint cache
- `pipedoc/capabilities/analyze.py` — Pipeline diagnosis
- `pipedoc/capabilities/review.py` — PR review

### Key Metrics
- Token reduction: 95%+
- Typical cost: $0.03/run
- Cache hit cost: $0.00
- Analysis time: ~2 seconds

---

## 🚀 You're Ready!

Pick a document above and start reading.

**Recommended first read:** [QUICKSTART.md](QUICKSTART.md) (5 minutes)

Then: `pip install -e .` and `pipedoc check`

Enjoy! 🎉
