# DECISION LOG

<!-- version: 2.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_OL_Report -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `docs/PROJECT_BRIEF.md` | Primary spec — highest authority |
> | Tier 2 | `null # No external FAQ` | Clarifications — cannot override Tier 1 |
> | Tier 3 | `docs/ADVERSARIAL_EVALUATION.md` | Advisory only — non-binding if inconsistent with Tier 1/2 |
> | Contract | This document | Implementation detail — subordinate to all tiers above |
>
> **Conflict rule:** When a higher-tier document and this contract disagree, the higher tier wins.
> Update this contract via `CONTRACT_CHANGE` or align implementation to the higher tier.

### Companion Contracts

**Upstream (this contract depends on):**
- None — decisions may reference any contract but have no structural dependency.

**Downstream (depends on this contract):**
- See [CHANGELOG](CHANGELOG.tmpl.md) for CONTRACT_CHANGE entries triggered by decisions (cross-reference ADR IDs)
- See [RISK_REGISTER](RISK_REGISTER.tmpl.md) for risk entries mitigated by decisions
- See [IMPLEMENTATION_PLAYBOOK](IMPLEMENTATION_PLAYBOOK.tmpl.md) §5 for change control procedure referencing ADR entries

## Purpose

This log records architectural and methodological decisions for the **Agent Security Red-Team Framework** project using a lightweight ADR (Architecture Decision Record) format. Each decision captures the context, alternatives, rationale, and consequences so that future changes are informed rather than accidental.

**Relationship to CHANGELOG:** When a decision triggers a `CONTRACT_CHANGE` commit, the change MUST also be logged in CHANGELOG with a cross-reference to the ADR ID.

---

## When to Create an ADR

Create a new ADR when:
- A decision affects multiple contracts or specs
- A decision resolves an ambiguity in authority documents
- A decision involves tradeoffs that future contributors need to understand
- A `CONTRACT_CHANGE` commit is triggered by a methodological choice
- A risk mitigation strategy is selected from multiple options

Do NOT create an ADR for routine implementation choices that follow directly from a single contract requirement with no alternatives.

---

## Status Lifecycle

```
Proposed → Accepted → [Superseded by ADR-YYYY]
```

- **Proposed:** Under discussion; not yet binding.
- **Accepted:** Binding; implementation may proceed.
- **Superseded:** Replaced by a newer ADR. MUST cite the superseding ADR ID. Do NOT delete superseded entries.

---

## Decision Record Template

Copy this block for each new decision:

```markdown
## ADR-XXXX: [Short title]

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-YYYY

### Context
[Problem statement and constraints. Cite authority documents by tier and section.]

### Decision
[The chosen approach. Be specific enough that someone can implement it without ambiguity.]

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | [approach] | **Accepted** | [why best] |
| B | [approach] | Rejected | [why not] |
| C | [approach] | Rejected | [why not] |

### Rationale
[Why this approach is best given the project constraints. Cite authority documents.]

### Consequences
[Tradeoffs and risks. Reference RISK_REGISTER entries if applicable.]

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| [contract name] | §N | [what changes] |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| [what to verify] | [command or file path] | [pass criteria] |
```

---

## Decisions

*(Record decisions below. Number sequentially: ADR-0001, ADR-0002, etc.)*

---

## ADR-0001: Agent target abstraction with framework-specific implementations

- **Date:** 2026-03-14
- **Status:** Accepted

### Context
PROJECT_BRIEF §7 requires testing attacks against 3 frameworks (LangChain, CrewAI, AutoGen). Each has a completely different API surface. Need a common interface so attacks are written once and run against all targets. (Tier 1 §3: "Open-source red-team framework" implies reusable architecture, not one-off scripts.)

### Decision
Abstract base class `AgentTarget` with 6 methods: `setup()`, `run_task()`, `reset()`, `get_system_prompt()`, `get_tools()`, `inject_context()`. Each framework gets its own implementation. Attacks interact ONLY through this interface.

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | ABC with per-framework implementations | **Accepted** | Attacks written once, N frameworks. Clean separation. |
| B | Direct framework calls in each attack script | Rejected | 5 attacks × 3 frameworks = 15 scripts. Duplication. |
| C | Adapter pattern with runtime dispatch | Rejected | Over-engineered for 3 targets. ABC is simpler. |

### Rationale
RQ2 requires demonstrating attacks across ≥2 frameworks. The abstraction makes this a config change, not a code change. Also enables the CLI tool (PROJECT_BRIEF §8: "pip install agent-redteam") to accept `--agent` flags cleanly.

### Consequences
- Each new framework target requires implementing 6 methods (~100 lines)
- Tests must cover the interface contract, not just one framework
- `inject_context()` and `get_conversation_history()` have framework-specific semantics

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| SCRIPT_ENTRYPOINTS_SPEC | §CLI flags | All scripts accept `--agent` flag |
| TEST_ARCHITECTURE | §integration | Per-framework smoke tests |
| CONFIGURATION_SPEC | §agents | Agent configs in config/agents/*.yaml |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| LangChain smoke test | `python scripts/smoke_test_agents.py --agent langchain` | PASS — tool call + correct answer |
| Dry-run all agents | `python scripts/smoke_test_agents.py --dry-run` | All 3 PASS |

---

## ADR-0002: Controlled tool suite instead of real tool access

- **Date:** 2026-03-14
- **Status:** Accepted

### Context
Red-teaming agents requires tools they can misuse. Using real tools (filesystem, network, shell) creates safety risks. Need tools that are interesting enough to demonstrate attacks but can't cause real harm. (PROJECT_BRIEF §3 Out of Scope: "Attacking production/deployed agents")

### Decision
In-memory tool suite: `calculator` (safe eval), `search_notes` (dict lookup), `file_reader`/`file_writer` (in-memory dict). `reset_tool_state()` clears state between scenarios. Tool data includes simulated sensitive content ("api_keys", "secret_plan") for red-team scenarios.

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | In-memory mock tools with simulated sensitive data | **Accepted** | Safe, deterministic, resettable |
| B | Sandboxed real filesystem (tempdir) | Rejected | Harder to reset, OS-dependent edge cases |
| C | Docker-isolated real tools | Rejected | Heavy infra for a research project |

### Rationale
Mock tools are sufficient to demonstrate all 5 attack classes. Tool misuse attacks target the permission boundary, not the tool implementation. In-memory tools give perfect determinism for multi-seed experiments.

### Consequences
- Findings may not generalize to real tool environments (acknowledged limitation)
- `reset_tool_state()` must be called between scenarios or memory poisoning bleeds across tests

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| ADVERSARIAL_EVALUATION | §3.1b Feature Controllability | Tool outputs = partially controllable |
| DATA_CONTRACT | §data sources | "Self-generated" — no external dataset |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| Tool isolation | Unit test: reset between scenarios | State cleared |
| Sensitive data accessible | `search_notes("api_keys")` returns result | Agent can find simulated secrets |

---

## ADR-0003: Anthropic Claude as primary LLM backend, OpenAI as secondary

- **Date:** 2026-03-14
- **Status:** Accepted

### Context
Agent targets need an LLM backend. PROJECT_BRIEF §7 says "Claude API or OpenAI API — configurable." Need to pick a primary for development velocity while maintaining portability.

### Decision
Anthropic Claude (claude-sonnet-4-20250514) as primary. `config/base.yaml` controls provider. LangChain abstracts the LLM layer — switching is a config change. Budget: ~$20-50 in tokens.

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | Claude primary, OpenAI secondary | **Accepted** | Brand alignment (AI Security Architecture on Anthropic stack), cost-effective with Sonnet |
| B | OpenAI primary | Rejected | No brand alignment, similar cost |
| C | Local LLM (Ollama) | Rejected | Weaker tool-calling, no GPU on VM. Stretch goal. |

### Rationale
Using Claude for red-teaming Claude-powered agents is the most authentic test. Blog post angle: "I red-teamed agents running on the same model family I used to build the framework." Also avoids OPENAI_API_KEY dependency for primary development.

### Consequences
- API costs tracked per-scenario in attack logs
- Must validate key findings on OpenAI backend before publishing (RQ generalization)

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| CONFIGURATION_SPEC | §base | `llm.provider` and `llm.model` fields |
| ENVIRONMENT_CONTRACT | §API keys | ANTHROPIC_API_KEY required |
