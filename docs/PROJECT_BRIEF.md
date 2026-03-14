# PROJECT BRIEF — Agent Security Red-Team Framework

<!-- version: 1.0 -->
<!-- created: 2026-03-14 -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `docs/PROJECT_BRIEF.md` | Primary spec — highest authority |
> | Tier 2 | — | No external FAQ (self-directed research) |
> | Tier 3 | `docs/ADVERSARIAL_EVALUATION.md` | Advisory — adversarial methodology |
> | Contract | This document | Implementation detail — subordinate to all tiers above |

---

## 1) Thesis Statement

**Autonomous AI agents have a systematically exploitable attack surface — prompt injection, tool misuse, privilege escalation, and memory poisoning — that can be discovered through structured red-teaming, and defended against using adversarial control analysis (the same architectural principle validated on IDS and vulnerability prediction).**

This is the third domain test for adversarial control analysis. If the methodology holds on agents (which have fundamentally different input/output structures than network flows or CVE metadata), it becomes a general security architecture principle — not a technique tied to any single domain.

---

## 2) Research Questions

| # | Question | How You'll Answer It | Success Criteria |
|---|----------|---------------------|-----------------|
| RQ1 | What is the attack taxonomy for autonomous AI agents? | Systematically enumerate attack classes by reviewing OWASP Top 10 for LLM, MITRE ATLAS, published agent exploits (LangChain CVEs, AutoGPT issues). Build an original taxonomy extending what exists. | Taxonomy covers ≥5 attack classes not in existing frameworks |
| RQ2 | Can these attacks be executed against real open-source agents? | Build attack scripts targeting LangChain ReAct agents, CrewAI multi-agent systems, and AutoGen. Run against controlled agent setups with measurable success rates. | ≥3 attack classes demonstrated with >50% success rate |
| RQ3 | Does adversarial control analysis apply to agent systems? | Classify agent inputs by controllability: user prompt (attacker-controlled), tool outputs (partially controllable), system prompt (defender-controlled), memory (poisonable). Evaluate robustness by input category. | Clear controllability matrix with measurable robustness differential |
| RQ4 | What architectural defenses reduce agent attack surface? | Design and test defenses: input sanitization, tool permission boundaries, memory integrity checks, output validation. Measure attack success before/after. | ≥2 defenses reduce attack success rate by >50% |

---

## 3) Scope Definition

### In Scope
- Attack taxonomy for autonomous AI agents (extending OWASP/ATLAS)
- Red-team scripts for 4+ attack classes against open-source agents
- Adversarial control analysis applied to agent input/output architecture
- Defensive architecture patterns with measured effectiveness
- Open-source red-team framework (CLI tool, not just scripts)

### Out of Scope
- Attacking production/deployed agents (only local controlled setups)
- Jailbreaking LLMs (prompt injection FOR agent misuse, not just harmful outputs)
- Training custom models (use existing LLMs as the agent backbone)
- Multi-agent coordination attacks (stretch goal only)

### Stretch Goals
- Multi-agent attack chains (Agent A compromises Agent B through shared tool)
- Benchmark suite that others can run against their own agents
- huntr submission if novel vulnerability discovered in LangChain/CrewAI/AutoGen

---

## 4) Data / Workload Definition

| Property | Value |
|----------|-------|
| **Primary "data"** | Self-generated: attack scenarios executed against controlled agent setups |
| **Agent frameworks** | LangChain (ReAct agent), CrewAI (multi-agent), AutoGen (Microsoft) |
| **LLM backend** | Claude API (Anthropic) or OpenAI API — configurable |
| **Download method** | pip install (langchain, crewai, autogen) |
| **Cost** | API calls — budget ~$20-50 in tokens for full evaluation |
| **Known issues** | Agent frameworks change rapidly; pin versions in environment.yml |

---

## 5) Skill Cluster Targets

| Cluster | Current Level | Target After Project | How This Project Advances It |
|---------|-------------|---------------------|---------------------------|
| **L** | L3+ | L3→L4 | Agent orchestration, tool-use patterns, multi-framework evaluation |
| **S** | S2+ | **S3** | Novel attack taxonomy + novel defense architecture. Third domain for adversarial control analysis. If published = S3 gate cleared. |
| **P** | P2++ | P2→P3-adj | CLI tool with pip install. Closer to "used by others" than notebooks. |
| **D** | D3+ | D3→D4 | Documented tradeoffs: which defenses break agent capability vs which preserve it |
| **V** | V1 | V1→V2 | Highest-traction blog post (agents are HOT). Conference CFP ready. |

---

## 6) Publication Target

| Property | Value |
|----------|-------|
| **Blog post title (working)** | "I Red-Teamed AI Agents: Here's How They Break (and How to Fix Them)" |
| **Content pillar** | AI Security Architecture (40% pillar) — PRIMARY pillar |
| **Conference CFP** | BSides / DEF CON AI Village — this IS the CFP submission project |
| **Target publish date** | Build now, publish when Hugo + Substack live |

---

## 7) Technical Approach

### Architecture Overview

```
Attack Taxonomy (OWASP + ATLAS + original)
    │
    ├── Attack Scripts (per attack class)
    │     prompt_injection.py
    │     tool_misuse.py
    │     privilege_escalation.py
    │     memory_poisoning.py
    │     output_manipulation.py
    │
    ├── Agent Targets (controlled setups)
    │     LangChain ReAct agent (tool-calling)
    │     CrewAI multi-agent (delegation)
    │     AutoGen (conversation-based)
    │
    ├── Adversarial Control Analysis
    │     Classify inputs: user prompt (attacker) vs
    │       system prompt (defender) vs tool output (partial)
    │       vs memory (poisonable)
    │     Measure robustness per input category
    │
    ├── Defense Evaluation
    │     input_sanitizer.py
    │     tool_permission_boundary.py
    │     memory_integrity_check.py
    │     output_validator.py
    │
    └── Results
          Attack success rates (before/after defense)
          Controllability matrix
          Architecture diagrams
          FINDINGS.md
```

### Key Technical Decisions (pre-project)

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Agent framework | LangChain only vs multi-framework | Multi (LC + CrewAI + AutoGen) | Shows attacks generalize across frameworks. Stronger finding. |
| LLM backend | Local (Ollama) vs API (Claude/OpenAI) | API with configurable backend | Faster iteration. Local = stretch goal for offline red-teaming. |
| Attack scope | Jailbreaks vs agent-specific | Agent-specific only | Jailbreaking is crowded. Agent tool misuse / privilege escalation is greenfield. |
| Framework | Scripts vs CLI tool | CLI tool (Click/Typer) | "pip install agent-redteam" = P3 evidence + adoption potential |

---

## 8) Definition of Done

- [ ] Attack taxonomy documented (≥5 classes beyond OWASP/ATLAS)
- [ ] ≥3 attack classes demonstrated against ≥2 agent frameworks
- [ ] Adversarial control analysis applied to agent I/O architecture
- [ ] ≥2 defensive patterns tested with measured effectiveness
- [ ] All code in version-controlled repo (GitHub)
- [ ] CLI tool installable via pip
- [ ] FINDINGS.md written with key results + architecture diagrams
- [ ] DECISION_LOG has all tradeoff decisions from every phase
- [ ] PUBLICATION_PIPELINE.md filled and blog draft started
- [ ] LESSONS_LEARNED.md in govML updated with FP-02 issues and wins
- [ ] Conference abstract ready for BSides / DEF CON AI Village CFP
