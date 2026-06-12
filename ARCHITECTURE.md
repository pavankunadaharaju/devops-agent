# pipedoc Architecture

**pipedoc** is a CLI-based DevOps agent for the CI lifecycle. This document outlines the complete system architecture, data flow, component interactions, and design principles.

---

## System Overview

```mermaid
graph TB
    subgraph CLI["CLI Layer"]
        click["CLI Commands<br/>click group"]
        auto["Auto-registered<br/>subcommands"]
    end
    
    subgraph Agent["Agent Core"]
        agentcore["Agent Class<br/>Orchestrator"]
        github["GitHub API Client<br/>github.py"]
        llm["LLM Interface<br/>llm.py"]
        cache["Cache Manager<br/>cache.py"]
    end
    
    subgraph Capabilities["Capability Plugins"]
        base["Base Capability ABC<br/>base.py"]
        analyze["Analyze<br/>Pipeline Diagnostics"]
        review["Review<br/>PR Analysis"]
        future["Future Capabilities<br/>fix, drift, postmortem"]
    end
    
    subgraph Processing["Processing Pipeline"]
        gather["gather()<br/>Fetch Raw Data"]
        distill["distill()<br/>Token-Efficient Reduction"]
        reason["reason()<br/>LLM Inference + Cache"]
        act["act()<br/>Output Rendering"]
    end
    
    subgraph External["External APIs"]
        ghapi["GitHub REST API"]
        models["GitHub Models API<br/>openai/gpt-4.1"]
    end
    
    subgraph Output["Output Layer"]
        terminal["Terminal Renderer<br/>Badges, Colors"]
        html["HTML Report<br/>Paper-style Design"]
    end
    
    click -->|registers| auto
    auto -->|instantiates| agentcore
    agentcore -->|uses| github
    agentcore -->|uses| llm
    agentcore -->|uses| cache
    
    analyze -->|extends| base
    review -->|extends| base
    future -->|extends| base
    
    base -->|defines| Processing
    
    gather -->|calls| github
    distill -->|filters| cache
    reason -->|calls| llm
    reason -->|checks| cache
    act -->|routes to| Output
    
    github -->|queries| ghapi
    llm -->|calls| models
    
    terminal -->|displays| user["User Terminal"]
    html -->|opens| browser["Browser/File"]
    
    style CLI fill:#e1f5e1
    style Agent fill:#e3f2fd
    style Capabilities fill:#fff3e0
    style Processing fill:#f3e5f5
    style External fill:#fce4ec
    style Output fill:#e0f2f1
```

---

## Component Architecture

### 1. **Core Layer** (`pipedoc/core/`)

```mermaid
graph LR
    subgraph GitHub["GitHub Module<br/>github.py"]
        parse["parse_url<br/>Extract owner/repo/id"]
        failed["failed_jobs<br/>List failures"]
        log["job_log<br/>Fetch logs"]
        diff["pr_diff<br/>Fetch diffs"]
        meta["pr_meta<br/>Metadata"]
    end
    
    subgraph LLM["LLM Module<br/>llm.py"]
        call["call<br/>Make inference"]
        parse_json["parse_json<br/>Extract JSON"]
        track["track_cost<br/>Telemetry"]
    end
    
    subgraph Filters["Filters Module<br/>filters.py"]
        error_win["error_window<br/>Extract context"]
        diff_file["diff_per_file<br/>Chunk diffs"]
        skip["SKIP_FILES<br/>Regex"]
        cap["MAX_CHARS=12000<br/>Hard limit"]
    end
    
    subgraph Cache["Cache Module<br/>cache.py"]
        finger["fingerprint<br/>SHA-256 hash"]
        norm["normalize<br/>Reduce variance"]
        store["store/load<br/>~/.pipedoc_cache.json"]
    end
    
    GitHub -->|"raw logs<br/>diffs"| Filters
    Filters -->|"windowed<br/>text"| Cache
    Cache -->|"fingerprint"| LLM
    LLM -->|"cached?"| Cache
    LLM -->|"call"| models["GitHub Models API"]
    
    style GitHub fill:#bbdefb
    style LLM fill:#bbdefb
    style Filters fill:#c8e6c9
    style Cache fill:#ffe0b2
```

### 2. **Capability System** (`pipedoc/capabilities/`)

```mermaid
graph TB
    subgraph Base["Base Capability ABC<br/>base.py"]
        context["Context<br/>raw, distilled, metadata<br/>reduction_pct"]
        finding["Finding<br/>title, detail, severity<br/>location, fix, confidence"]
        result["Result<br/>capability, findings<br/>tokens_used, cost_usd"]
    end
    
    subgraph CapInterface["Capability Interface"]
        gather_i["gather()<br/>Fetch GitHub data"]
        distill_i["distill()<br/>Filter & normalize"]
        reason_i["reason()<br/>LLM call + cache"]
        act_i["act()<br/>Render output"]
    end
    
    subgraph Analyze["Analyze Capability<br/>analyze.py"]
        a_gather["gather(): failed_jobs<br/>job_log"]
        a_distill["distill(): error_window<br/>± 8 lines, last 40"]
        a_reason["reason(): root_cause<br/>JSON: root_cause,<br/>explanation, fix, confidence"]
        a_act["act(): Terminal/HTML<br/>Severity badges"]
    end
    
    subgraph Review["Review Capability<br/>review.py"]
        r_gather["gather(): pr_diff<br/>pr_meta, context"]
        r_distill["distill(): diff_per_file<br/>skip lock/vendor,<br/>cap per-file"]
        r_reason["reason(): review findings<br/>JSON: findings[]<br/>file, line, severity, comment"]
        r_act["act(): Terminal/HTML<br/>Diff-style output"]
    end
    
    Base -->|"defines"| CapInterface
    CapInterface -->|"implemented by"| Analyze
    CapInterface -->|"implemented by"| Review
    
    a_gather --> a_distill
    a_distill --> a_reason
    a_reason --> a_act
    
    r_gather --> r_distill
    r_distill --> r_reason
    r_reason --> r_act
    
    Finding -->|"produced by"| a_reason
    Finding -->|"produced by"| r_reason
    Result -->|"aggregates"| Finding
    
    style Base fill:#fff9c4
    style CapInterface fill:#f0f4c3
    style Analyze fill:#c8e6c9
    style Review fill:#c8e6c9
```

---

## Data Flow Diagrams

### Pipeline Failure Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Agent
    participant GitHub as GitHub API
    participant Cache
    participant LLM as GitHub Models
    participant Render
    
    User->>CLI: pipedoc analyze <run_url>
    CLI->>Agent: create & execute
    Agent->>GitHub: parse_url() + failed_jobs()
    GitHub-->>Agent: job list
    Agent->>GitHub: job_log(job_id)
    GitHub-->>Agent: raw log (50KB+)
    Agent->>Agent: error_window() + normalize()
    Agent-->>Agent: windowed text (1KB)
    Agent->>Cache: fingerprint(text)
    Cache-->>Agent: hash + lookup
    alt Cache Hit
        Cache-->>Agent: cached result
        Agent->>Render: Finding(cached=true)
    else Cache Miss
        Agent->>LLM: call(messages, temp=0.2)
        LLM->>GitHub: inference request
        GitHub-->>LLM: JSON response
        LLM-->>Agent: parsed result
        Agent->>Cache: store(hash, result)
        Agent->>Render: Finding(cached=false)
    end
    Render->>User: Terminal + HTML + cost telemetry
```

### PR Review Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Agent
    participant GitHub as GitHub API
    participant Cache
    participant LLM as GitHub Models
    participant Render
    
    User->>CLI: pipedoc review <pr_url> --report
    CLI->>Agent: create & execute
    Agent->>GitHub: pr_diff(pr_number)
    GitHub-->>Agent: unified diff (100KB+)
    Agent->>Agent: diff_per_file() + skip_files()
    Agent->>Agent: chunk per file, cap size
    Agent-->>Agent: filtered diffs (5KB)
    Agent->>GitHub: pr_meta(pr_number)
    GitHub-->>Agent: metadata (title, desc, commits)
    Agent->>Cache: fingerprint(diffs + meta)
    Cache-->>Agent: hash + lookup
    alt Cache Hit
        Cache-->>Agent: cached findings
    else Cache Miss
        Agent->>LLM: call(chunked_diffs, temp=0.2)
        LLM-->>Agent: findings JSON
        Agent->>Cache: store(hash, findings)
    end
    Agent->>Render: generate HTML report
    Render->>User: Terminal output + HTML file + browser open
```

---

## 4-Step Capability Lifecycle

Every capability implements this contract:

```mermaid
graph TB
    subgraph Lifecycle["4-Step Lifecycle"]
        direction LR
        G["1. gather()<br/>Fetch raw data<br/>from GitHub APIs"]
        D["2. distill()<br/>Token-efficient<br/>reduction<br/>MANDATORY"]
        R["3. reason()<br/>Cache-aware<br/>LLM call(s)"]
        A["4. act()<br/>Render output<br/>terminal/HTML"]
    end
    
    G -->|"raw context"| D
    D -->|"<12K chars"| R
    R -->|"cache check<br/>LLM call"| A
    A -->|"telemetry<br/>Finding[]"| Result["Result<br/>context +<br/>findings +<br/>tokens +<br/>cost"]
    
    subgraph Distill_Detail["Distill Principles"]
        local["Local pre-filtering<br/>no LLM"]
        regex["Regex patterns<br/>error/fatal/traceback"]
        normalize["Normalize<br/>hash variance"]
        cap["Hard cap<br/>12,000 chars"]
        efficient["~95%<br/>reduction"]
    end
    
    D -->|"implements"| Distill_Detail
    
    style Lifecycle fill:#e1bee7
    style Result fill:#ffe0b2
    style Distill_Detail fill:#c5e1a5
```

---

## Token-Efficiency Strategy

```mermaid
graph LR
    subgraph Input["Input<br/>Raw Log 50KB"]
        raw["Raw text"]
    end
    
    subgraph LocalFilter["Local Pre-Filter<br/>No LLM Cost"]
        regex["Regex extraction<br/>error/fatal/traceback<br/>±8 lines context"]
        last["Keep last 40 lines<br/>Often root cause"]
        cap["Cap 12,000 chars<br/>Hard limit"]
    end
    
    subgraph Normalization["Normalization<br/>Reduce Variance"]
        hashes["<hash> for URLs"]
        lines["line <n> for line nums"]
        paths["<tmp> for temp paths"]
    end
    
    subgraph Fingerprint["Fingerprint Cache<br/>SHA-256"]
        cache["Lookup fingerprint"]
        hit["CACHE HIT<br/>$0.00<br/>Zero LLM calls"]
        miss["CACHE MISS<br/>LLM call<br/>~2,100 tokens"]
    end
    
    subgraph Telemetry["Cost Telemetry"]
        before["Chars before:<br/>50,000"]
        after["Chars after:<br/>1,200"]
        pct["Reduction:<br/>97.6%"]
        cost["Cost: $0.02<br/>vs $0.96 naive"]
    end
    
    Input -->|"apply"| LocalFilter
    LocalFilter -->|"normalize"| Normalization
    Normalization -->|"hash"| Fingerprint
    Fingerprint -->|"hit or miss"| miss
    Fingerprint -->|"hit"| hit
    miss -->|"track"| Telemetry
    
    style Input fill:#ffcdd2
    style LocalFilter fill:#c8e6c9
    style Normalization fill:#c8e6c9
    style Fingerprint fill:#ffe0b2
    style Telemetry fill:#b3e5fc
    style hit fill:#a5d6a7
```

---

## CLI Structure & Auto-Registration

```mermaid
graph TB
    subgraph Entry["Entry Point"]
        console["console_script: pipedoc<br/>in pyproject.toml"]
    end
    
    subgraph CLISetup["CLI Setup<br/>cli.py"]
        main["@click.group()<br/>main()"]
        init["init_agent()<br/>Load token, config"]
    end
    
    subgraph Registry["Capability Registry<br/>capabilities/__init__.py"]
        all["ALL = [Analyze, Review]"]
        register["for cap in ALL:<br/>@main.command(cap.name)"]
    end
    
    subgraph Commands["Auto-Registered Commands"]
        analyze["$ pipedoc analyze"]
        review["$ pipedoc review"]
        future["$ pipedoc fix<br/>$ pipedoc drift"]
    end
    
    subgraph Execution["Execution"]
        exec["execute_capability()<br/>gather → distill →<br/>reason → act"]
    end
    
    console -->|"calls"| CLISetup
    CLISetup -->|"imports"| Registry
    Registry -->|"registers"| Commands
    Commands -->|"dispatch"| Execution
    
    style Entry fill:#f8bbd0
    style CLISetup fill:#f0f4c3
    style Registry fill:#fff9c4
    style Commands fill:#b2dfdb
    style Execution fill:#b2ebf2
```

---

## Data Models

```mermaid
graph TB
    subgraph Context["Context<br/>Represents raw + distilled state"]
        ctx_raw["raw: str<br/>Original GitHub data"]
        ctx_distilled["distilled: str<br/>Token-filtered"]
        ctx_meta["metadata: dict<br/>url, owner, repo, etc"]
        ctx_prop["reduction_pct: property<br/>len(raw) - len(distilled) / len(raw)"]
    end
    
    subgraph Finding["Finding<br/>Single diagnostic result"]
        f_title["title: str"]
        f_detail["detail: str"]
        f_severity["severity:<br/>info|low|med|high"]
        f_location["location: str<br/>file:line or job"]
        f_fix["suggested_fix: str"]
        f_confidence["confidence:<br/>high|med|low"]
        f_cached["cached: bool"]
    end
    
    subgraph Result["Result<br/>Full capability output"]
        r_cap["capability: str"]
        r_findings["findings: List[Finding]"]
        r_context["context: Context"]
        r_tokens["tokens_used: int"]
        r_cost["cost_usd: float"]
    end
    
    Context -.->|"aggregated in"| Result
    Finding -->|"List in"| Result
    
    style Context fill:#c5cae9
    style Finding fill:#ffccbc
    style Result fill:#c8e6c9
```

---

## Output Rendering Pipeline

```mermaid
graph TB
    subgraph Result["Result Object"]
        findings["findings: List[Finding]"]
        context["context: Context"]
        cost["cost_usd"]
    end
    
    subgraph Render["render.py<br/>Renderer"]
        terminal["Terminal Output"]
        html["HTML Report"]
    end
    
    subgraph TerminalOutput["Terminal Output<br/>Click-based"]
        badge_sev["Severity badges<br/>🔴 HIGH 🟡 MED"]
        badge_cached["💾 CACHED marker"]
        context_line["Reduction: 50K→1K (98%)"]
        footer["Session telemetry:<br/>tokens | cost"]
    end
    
    subgraph HTMLReport["HTML Report<br/>Standalone file"]
        design["Paper aesthetic<br/>pale-green stripes<br/>tractor-feed holes"]
        stamps["Rubber-stamp badges<br/>FAILED, CACHE HIT"]
        cost_strip["Cost strip (top):<br/>raw→sent→%→tokens→$"]
        diffs["Diff-style fixes<br/>with monospace"]
        fonts["IBM Plex Mono<br/>+ Archivo"]
        colors["Palette:<br/>paper #F7F8F2<br/>stripe #E4EFE1<br/>ink #1E2A23"]
    end
    
    Result -->|"consume"| Render
    Render -->|"generates"| TerminalOutput
    Render -->|"generates"| HTMLReport
    TerminalOutput -->|"print to stdout"| User["User sees"]
    HTMLReport -->|"write file +<br/>open browser"| Browser["Browser opens"]
    
    style Result fill:#fff9c4
    style Render fill:#f0f4c3
    style TerminalOutput fill:#c5e1a5
    style HTMLReport fill:#ffccbc
```

---

## Configuration & Initialization

```mermaid
graph LR
    subgraph Input["Input Sources"]
        env["GITHUB_TOKEN<br/>env var"]
        cli["--token CLI flag"]
        config["~/.pipedoc/config.yaml<br/>default model, etc"]
    end
    
    subgraph Agent["Agent Initialization<br/>agent.py"]
        pat["Resolve PAT<br/>env > CLI > config"]
        token_check["Verify: GitHub Models<br/>connectivity check"]
        cache_init["Load ~/.pipedoc_cache.json"]
        gh_init["Initialize GitHub client"]
        llm_init["Initialize LLM client<br/>default model: openai/gpt-4.1"]
    end
    
    subgraph Ready["Ready State"]
        agentobj["Agent object<br/>with auth + cache"]
    end
    
    env -->|"priority 1"| Agent
    cli -->|"priority 2"| Agent
    config -->|"priority 3"| Agent
    
    Agent -->|"setup"| Ready
    
    style Input fill:#ffccbc
    style Agent fill:#c8e6c9
    style Ready fill:#b2dfdb
```

---

## Error Handling & Resilience

```mermaid
graph TB
    subgraph Scenario["Failure Scenarios"]
        github_fail["GitHub API fails"]
        token_invalid["PAT invalid"]
        models_disabled["Models API disabled<br/>by org admin"]
        rate_limit["Rate limit exceeded"]
        parse_error["JSON parse error<br/>from LLM"]
    end
    
    subgraph Handling["Handling Strategy"]
        log["Log with context"]
        user_msg["Clear user message<br/>why it failed"]
        retry["Retry logic<br/>with backoff"]
        fallback["Fallback: shell copilot CLI<br/>if Models unavailable"]
    end
    
    subgraph Recovery["Recovery"]
        cache_use["Use cache if available"]
        partial["Partial result"]
        retry_later["Suggest retry later"]
    end
    
    Scenario -->|"caught"| Handling
    Handling -->|"attempt"| Recovery
    
    style Scenario fill:#ffccbc
    style Handling fill:#fff9c4
    style Recovery fill:#c5e1a5
```

---

## Extension Points (Future Capabilities)

```mermaid
graph TB
    subgraph Current["Current Capabilities"]
        analyze["Analyze"]
        review["Review"]
    end
    
    subgraph Future["Future Capabilities<br/>Same 4-step lifecycle"]
        fix["fix<br/>gather: diagnosis<br/>distill: action plan<br/>reason: generate PR<br/>act: open MR"]
        
        drift["drift<br/>gather: live cluster<br/>distill: delta<br/>reason: explain drift<br/>act: suggest ArgoCD"]
        
        postmortem["postmortem<br/>gather: alerts + timeline<br/>distill: key events<br/>reason: draft report<br/>act: render markdown"]
        
        gitlab["GitLab CI<br/>gather: gitlab API<br/>distill: same filters<br/>reason: LLM<br/>act: gitlab comments"]
    end
    
    subgraph AddCapability["To Add a New Capability"]
        step1["1. Create pipedoc/capabilities/new_cap.py"]
        step2["2. Subclass Capability ABC"]
        step3["3. Implement 4-step lifecycle"]
        step4["4. Add to ALL list in __init__.py"]
        step5["CLI auto-registers!"]
    end
    
    Current -->|"existing"| Current
    Current -->|"extends to"| Future
    Future -->|"follow"| AddCapability
    
    style Current fill:#c8e6c9
    style Future fill:#ffe0b2
    style AddCapability fill:#b3e5fc
```

---

## Deployment & Distribution

```mermaid
graph LR
    subgraph Build["Build"]
        src["Source code<br/>pyproject.toml"]
        package["pip install -e ."]
    end
    
    subgraph Dist["Distribution"]
        PyPI["PyPI publish<br/>pip install pipedoc"]
        local["Local installation<br/>git clone + pip install"]
    end
    
    subgraph User["User Environment"]
        token["export GITHUB_TOKEN=ghp_xxx"]
        cache_dir["~/.pipedoc/"]
        commands["$ pipedoc analyze/review/..."]
    end
    
    Build -->|"package"| Dist
    Dist -->|"install"| User
    User -->|"execute"| commands
    
    style Build fill:#bbdefb
    style Dist fill:#c8e6c9
    style User fill:#ffe0b2
```

---

## Security & Permissions

```mermaid
graph TB
    subgraph Token["GitHub PAT Scope"]
        pat_required["Required minimum:<br/>repo (read)<br/>actions (read)<br/>models (read)"]
        pat_optional["Optional:<br/>admin:repo_hook<br/>workflow"]
    end
    
    subgraph Protection["Data Protection"]
        cache_local["Cache: local disk<br/>~/.pipedoc_cache.json<br/>not transmitted"]
        token_env["Token: env var<br/>never logged"]
        tls["TLS to GitHub<br/>all API calls"]
    end
    
    subgraph Access["Access Control"]
        owner_only["User owns token<br/>responsible for scope"]
        team_cache["(Future) team cache<br/>DynamoDB/Redis"]
    end
    
    Token -->|"governs"| Protection
    Protection -->|"enforced by"| Access
    
    style Token fill:#ffccbc
    style Protection fill:#c8e6c9
    style Access fill:#b3e5fc
```

---

## Performance Characteristics

| Scenario | Time | Tokens | Cost | Notes |
|----------|------|--------|------|-------|
| Analyze (cache miss) | ~2s | 2,100 | $0.02 | Includes GitHub API calls |
| Analyze (cache hit) | ~100ms | 0 | $0.00 | Fingerprint lookup only |
| Review small PR (miss) | ~3s | 3,500 | $0.03 | <5 files, <10KB diff |
| Review large PR (miss) | ~5s | 6,800 | $0.06 | >20 files, >50KB diff |
| Review (cache hit) | ~100ms | 0 | $0.00 | Fingerprint lookup |

---

## Deployment Checklist

- [ ] `pyproject.toml` defines package + console script
- [ ] `pipedoc/core/github.py` — GitHub client (parse, jobs, logs, diffs)
- [ ] `pipedoc/core/llm.py` — GitHub Models client + cost tracking
- [ ] `pipedoc/core/filters.py` — error_window, diff_per_file, SKIP_FILES
- [ ] `pipedoc/core/cache.py` — fingerprint, Cache class
- [ ] `pipedoc/capabilities/base.py` — Capability ABC, Context/Finding/Result
- [ ] `pipedoc/capabilities/analyze.py` — 4-step pipeline diagnosis
- [ ] `pipedoc/capabilities/review.py` — 4-step PR review
- [ ] `pipedoc/capabilities/__init__.py` — ALL registry + CLI registration
- [ ] `pipedoc/cli.py` — click group, auto-registration
- [ ] `pipedoc/agent.py` — Agent orchestrator
- [ ] `pipedoc/render.py` — Terminal + HTML rendering
- [ ] Test with real GitHub token (Actions run + PR)
- [ ] Generate HTML report from mock; verify design
- [ ] Cost telemetry live on screen

---

## References

- **GitHub Models API:** https://models.github.ai/inference/chat/completions
- **GitHub REST API Docs:** https://docs.github.com/en/rest
- **Click Documentation:** https://click.palletsprojects.com/
- **Mermaid Diagram Syntax:** https://mermaid.js.org/
