# Agent Security Red-Team Framework — Claude Code Context

> **govML v2.4** | Profile: security-ml (21 templates)

## Project Purpose

Build an open-source framework for systematically red-teaming autonomous AI agents — discovering prompt injection, tool misuse, privilege escalation, and memory poisoning vulnerabilities. Apply adversarial control analysis (third domain validation after IDS + CVE prediction).

- **Context:** Self-directed research (FP-02 in frontier project pipeline)
- **Profile:** security-ml
- **Python:** 3.11 | **Env:** agent-redteam
- **Brand pillar:** AI Security Architecture (40% pillar) — PRIMARY
- **Blog title (working):** "I Red-Teamed AI Agents: Here's How They Break (and How to Fix Them)"
- **Tagline alignment:** "Building AI systems that survive adversaries" — this project proves which agents DON'T survive

## Authority Hierarchy

| Tier | Source | Path |
|------|--------|------|
| 1 (highest) | Project Brief — thesis, RQs, scope | `docs/PROJECT_BRIEF.md` |
| 2 | — | No external FAQ |
| 3 | Adversarial evaluation methodology | `docs/ADVERSARIAL_EVALUATION.md` |
| Contracts | Governance docs | `docs/*.md` |

## Current Phase

**Phase:** 1 — Attack Taxonomy & Baselines

### Phase Progression

| Phase | Name | Status |
|-------|------|--------|
| 0 | Environment & Agent Setup | **COMPLETE** (smoke test passed 2026-03-14) |
| 1 | Attack Taxonomy & Baselines | **CURRENT** |
| 2 | Red-Team Execution | Not started |
| 3 | Adversarial Control Analysis + Defenses | Not started |
| 4 | Findings & Publication Draft | Not started |

## Research Questions

| # | Question | Key |
|---|----------|-----|
| RQ1 | What is the attack taxonomy for autonomous AI agents? | ≥5 novel classes beyond OWASP/ATLAS |
| RQ2 | Can attacks be executed against real open-source agents? | ≥3 classes demonstrated, >50% success |
| RQ3 | Does adversarial control analysis apply to agents? | Controllability matrix + robustness differential |
| RQ4 | What defenses reduce agent attack surface? | ≥2 defenses, >50% reduction |

## Agent Targets

| Framework | Type | Install |
|-----------|------|---------|
| LangChain | ReAct agent (tool-calling) | `pip install langchain langchain-openai` |
| CrewAI | Multi-agent (delegation) | `pip install crewai` |
| AutoGen | Conversation-based | `pip install autogen-agentchat` |

## Key Files

| File | Purpose |
|------|---------|
| `docs/PROJECT_BRIEF.md` | **READ FIRST** — thesis, 4 RQs, scope, architecture |
| `docs/PUBLICATION_PIPELINE.md` | Blog post governance + distribution |
| `docs/DECISION_LOG.md` | All tradeoff decisions (mandatory at every phase gate) |
| `docs/ADVERSARIAL_EVALUATION.md` | Attack methodology + controllability matrix |
| `src/attacks/` | Attack scripts per attack class |
| `src/defenses/` | Defensive pattern implementations |
| `src/agents/` | Controlled agent target setups |

## AI Division of Labor

### Permitted
- Code generation for attack scripts, defense patterns, agent setups
- Test generation and execution
- Attack taxonomy research (reviewing OWASP, ATLAS, published CVEs)
- Architecture diagram generation
- CLI tool scaffolding (Click/Typer)

### Prohibited
- Attacking production/deployed agents or services
- Generating actual malicious payloads for real-world use
- Writing the interpretation of WHY certain attacks succeed (human insight)
- Modifying PROJECT_BRIEF thesis or research questions
- Deciding which attacks are "interesting" (that's the practitioner judgment)

## Conventions

- **Seeds:** [42, 123, 456] — for any stochastic elements
- **Smoke test first:** Run each attack on a minimal agent before full evaluation
- **Decisions:** Log in DECISION_LOG at every phase gate (mandatory per v2.4)
- **API costs:** Track token usage. Budget: ~$20-50 total.
- **Pin framework versions:** Agent frameworks change weekly. Pin in environment.yml.
- **Adversarial control analysis:** Classify every agent input by controllability BEFORE designing attacks
