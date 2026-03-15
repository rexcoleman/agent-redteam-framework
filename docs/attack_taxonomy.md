# Agent Attack Taxonomy — FP-02

> **Authority:** Subordinate to PROJECT_BRIEF (Tier 1) RQ1
> **Success criterion:** ≥5 attack classes not covered by OWASP LLM Top 10 or MITRE ATLAS
> **Created:** 2026-03-14
> **Status:** DRAFT — pre-registration for Phase 2 execution

---

## Existing Framework Coverage

### OWASP Top 10 for LLM Applications (2025)
| # | Category | Agent-Specific? |
|---|----------|----------------|
| LLM01 | Prompt Injection | Partially — covers direct/indirect but NOT agent-specific tool chain injection |
| LLM02 | Insecure Output Handling | Yes — relevant to agent output parsing |
| LLM03 | Training Data Poisoning | No — we don't train models |
| LLM04 | Model Denial of Service | Peripheral |
| LLM05 | Supply Chain Vulnerabilities | Out of scope |
| LLM06 | Sensitive Information Disclosure | Yes — via tool access |
| LLM07 | Insecure Plugin Design | **Directly relevant** — agents use tools/plugins |
| LLM08 | Excessive Agency | **Core target** — agents act autonomously |
| LLM09 | Overreliance | Human factor, not technical attack |
| LLM10 | Model Theft | Out of scope |

**Gap:** OWASP covers LLM-level vulnerabilities but NOT agent orchestration-level attacks (multi-step reasoning chains, cross-agent delegation, persistent memory manipulation).

### MITRE ATLAS (Adversarial Threat Landscape for AI Systems)
Covers ML model attacks (evasion, poisoning, extraction) but has minimal coverage of:
- Agent-specific tool misuse patterns
- Multi-agent delegation attacks
- Memory/context persistence attacks
- Autonomous decision-chain manipulation

---

## Agent-Specific Attack Taxonomy

### Classification Axes

**By target surface:**
- Input surface: user prompt, system prompt, tool outputs, memory/context
- Processing surface: reasoning chain, tool selection, output formatting
- State surface: conversation history, persistent memory, cross-agent state

**By controllability (adversarial control analysis):**

| Input Type | Controllability | Examples |
|-----------|----------------|---------|
| User prompt | **Attacker-controlled** | Direct text input to agent |
| Tool outputs | **Partially controllable** | Attacker poisons data source that tool reads |
| System prompt | **Defender-controlled** | Agent instructions, role definition |
| Model weights | **Defender-controlled** | LLM parameters (not modifiable at runtime) |
| Conversation history | **Poisonable** | Prior turns, injected context |
| Cross-agent messages | **Partially controllable** | Messages between agents in multi-agent systems |

---

## Attack Classes

### Class 1: Direct Prompt Injection (EXISTING — OWASP LLM01)
**What:** Attacker crafts user input that overrides agent instructions.
**Existing coverage:** OWASP LLM01, well-documented.
**Agent-specific twist:** Agent prompt injection targets TOOL SELECTION, not just text output. Making an agent call the wrong tool or pass wrong parameters is fundamentally different from making a chatbot say something harmful.
**Variants:**
- 1a: Instruction override ("Ignore previous instructions and...")
- 1b: Role hijacking ("You are now a different agent that...")
- 1c: Tool-forcing ("You must use the file_writer tool to write...")

### Class 2: Indirect Prompt Injection via Tool Outputs (PARTIALLY NEW)
**What:** Attacker controls data that a tool returns, embedding instructions in tool output that the agent follows.
**Existing coverage:** Mentioned in OWASP LLM01 (indirect), but NOT with agent tool chains.
**Novel aspect:** In agents, tool outputs feed back into the reasoning loop. A poisoned tool output can redirect the ENTIRE remaining chain of tool calls.
**Variants:**
- 2a: Data source poisoning (notes database contains injected instructions)
- 2b: File content injection (file contains prompt injection payload)
- 2c: Cascading tool manipulation (tool A output causes agent to call tool B with attacker-controlled params)

### Class 3: Tool Permission Boundary Violation (Systematized — not in OWASP/ATLAS)
**What:** Agent is tricked into using tools beyond its intended scope or with unauthorized parameters.
**Agent-specific framing:** OWASP LLM07 covers "insecure plugin design" (the tool is insecure). This class covers **the agent using a secure tool insecurely** — the tool works correctly but the agent's use of it violates intended boundaries. The concept of tool misuse is well-known; this systematizes it for the agent context.
**Variants:**
- 3a: Parameter escalation (agent passes dangerous parameters to a safe tool)
- 3b: Tool chain abuse (agent chains tools in unintended sequence to achieve unauthorized action)
- 3c: Implicit permission assumption (agent assumes it has permission because no explicit denial)

### Class 4: Cross-Agent Privilege Escalation (Systematized — not in OWASP/ATLAS)
**What:** In multi-agent systems, a compromised or manipulated agent delegates tasks to other agents, escalating privileges across the system.
**Agent-specific framing:** Privilege escalation is a well-known security concept. OWASP/ATLAS focus on single-model attacks. Multi-agent delegation as a privilege escalation vector is the agent-specific framing not covered by existing frameworks.
**Variants:**
- 4a: Delegation abuse (researcher agent tricks writer agent into writing to unauthorized locations)
- 4b: Role confusion (agent assumes another agent's permissions during delegation)
- 4c: Message injection (attacker injects messages into cross-agent communication channel)

### Class 5: Memory/Context Poisoning (Systematized — not in OWASP/ATLAS)
**What:** Attacker manipulates the agent's conversation history, persistent memory, or shared context to influence future behavior.
**Agent-specific framing:** Data poisoning is a well-known attack concept. The agent-specific dimension is that stateless LLM attacks reset each turn, while agents with memory carry poisoned state forward, making single injections persistent.
**Variants:**
- 5a: History injection (inject fake prior turns into conversation history)
- 5b: Context window manipulation (fill context window to push out system prompt / safety instructions)
- 5c: Persistent backdoor (inject instruction into persistent memory that activates on trigger)

### Class 6: Reasoning Chain Hijacking (Novel pattern — not in OWASP/ATLAS)
**What:** Attacker manipulates the agent's multi-step reasoning process, not just the final output. Targets the ReAct loop (Thought → Action → Observation cycle).
**Why this is the strongest novelty claim:** OWASP focuses on input to output. Agent reasoning chains are multi-step — attacking the REASONING PROCESS via structured step-by-step instructions that look like legitimate tasks is a distinct, previously unnamed attack pattern. Unlike prompt injection (well-documented) or data poisoning (well-known concept), reasoning chain hijacking exploits the agent's core capability as the attack vector, and no existing framework names or addresses it.
**Variants:**
- 6a: Thought injection (influence the agent's "thinking" step to change tool selection)
- 6b: Observation override (make the agent misinterpret a tool's output)
- 6c: Loop manipulation (cause the agent to enter infinite tool-calling loops or skip steps)

### Class 7: Output Format Exploitation (Systematized — not in OWASP/ATLAS)
**What:** Attacker exploits how agent outputs are parsed by downstream systems. Agents produce structured output (JSON, function calls) that other systems consume — format manipulation can bypass downstream security.
**Agent-specific framing:** Output manipulation is a known concept (cf. OWASP LLM02 Insecure Output Handling). The agent-specific dimension is that agent output includes structured data (tool calls, JSON, API parameters) consumed by code, not just text consumed by humans.
**Variants:**
- 7a: JSON injection (inject malicious fields into structured agent output)
- 7b: Tool call spoofing (make agent output look like a tool call to downstream parser)
- 7c: Delimiter manipulation (break structured output format to inject content)

---

## Novelty Assessment

| Class | In OWASP? | In ATLAS? | Status | Implementable in FP-02? |
|-------|-----------|-----------|--------|------------------------|
| 1: Direct Prompt Injection | Yes (LLM01) | Partial | Known — baseline | Yes (reference) |
| 2: Indirect via Tool Outputs | Partial (LLM01) | No | **Partially known** — agent tool chain context adds specificity | Yes |
| 3: Tool Permission Boundary | Partial (LLM07) | No | **Systematized** — concept of tool misuse exists; agent USE of secure tools insecurely is the agent-specific framing | Yes |
| 4: Cross-Agent Privilege Escalation | No | No | **Systematized** — privilege escalation is well-known; multi-agent delegation context is the agent-specific framing | Yes (CrewAI) |
| 5: Memory/Context Poisoning | No | No | **Systematized** — data poisoning is well-known; persistent agent memory as attack surface is the agent-specific framing | Yes |
| 6: Reasoning Chain Hijacking | No | No | **Novel pattern** — exploiting the ReAct reasoning loop via structured instructions is a distinct, previously unnamed attack pattern | Yes |
| 7: Output Format Exploitation | Partial (LLM02) | No | **Systematized** — output manipulation is known; structured agent output (JSON, tool calls) consumed by code is the agent-specific framing | Yes |

**Classes not covered by OWASP/ATLAS: 5** (Classes 3, 4, 5, 6, 7). Of these, reasoning chain hijacking (Class 6) is the strongest novelty claim as a named attack pattern. Classes 3, 4, 5, and 7 systematize known security concepts (tool misuse, privilege escalation, data poisoning, output manipulation) into an agent-specific taxonomy.

---

## Controllability Matrix (Adversarial Control Analysis)

| Attack Class | Primary Input | Controllability | Defender Can Observe? | Defense Difficulty |
|-------------|--------------|----------------|----------------------|-------------------|
| 1: Direct Injection | User prompt | Attacker-controlled | Yes (input filtering) | Low |
| 2: Indirect Injection | Tool output | Partially controllable | Partial (tool output logging) | Medium |
| 3: Tool Boundary | User prompt → tool params | Attacker-controlled | Yes (parameter validation) | Medium |
| 4: Cross-Agent | Cross-agent messages | Partially controllable | Partial (message logging) | High |
| 5: Memory Poisoning | Conversation history | Poisonable | Partial (history audit) | High |
| 6: Reasoning Hijacking | Reasoning chain | Partially controllable | Low (internal state) | Very High |
| 7: Output Format | Agent output | Agent-generated | Yes (output validation) | Medium |

**Key insight:** Attack difficulty correlates inversely with defender observability. Classes 5 and 6 are hardest to defend because the attack surface (memory, reasoning) is internal to the agent and not easily inspectable.

---

## Implementation Priority (Phase 2)

| Priority | Class | Why |
|----------|-------|-----|
| **P0** | 1: Direct Injection | Baseline — calibrate attack success rate on known vector |
| **P0** | 2: Indirect via Tools | Highest practical risk — tool outputs are the primary agent input |
| **P1** | 3: Tool Boundary | Demonstrates "agent misuses secure tool" — novel finding |
| **P1** | 5: Memory Poisoning | Demonstrates persistence — strongest novelty signal |
| **P2** | 6: Reasoning Hijacking | Hardest to implement, highest novelty |
| **P2** | 4: Cross-Agent | Requires CrewAI multi-agent setup |
| **P3** | 7: Output Format | Requires downstream consumer — lower priority |

---

## Revision Log

| Date | Change |
|------|--------|
| 2026-03-14 | Initial taxonomy: 7 classes, 5 not covered by OWASP/ATLAS |
| 2026-03-15 | Novelty calibration: Classes 3-5, 7 reframed as "systematized from existing concepts"; Class 6 (reasoning chain hijacking) retained as strongest novelty claim |
