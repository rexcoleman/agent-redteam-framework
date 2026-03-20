# I red-teamed LangChain and CrewAI agents with 19 attack scenarios — reasoning chain hijacking achieves 100% success and partially evades every defense

I sent 19 attack scenarios at a default-configured LangChain ReAct agent powered by Claude Sonnet. 13 succeeded (68% overall). Prompt injection on CrewAI showed the same 80% rate. The most dangerous attack class — reasoning chain hijacking — hit 100% success across 3 seeds and partially evades every defense I built, including an LLM-as-judge layer. These are default agent configurations; production-hardened setups would likely do better.

I systematized 7 attack classes into a reusable taxonomy. Two exist in current frameworks (OWASP LLM Top 10, MITRE ATLAS). Five target agent-specific surfaces that model-level taxonomies miss — because agents reason, use tools, maintain memory, and delegate. The reasoning loop is both the feature and the attack surface.

Key findings:

- **Reasoning chain hijacking: 100% success** — the attack embeds exfiltration steps in a legitimate-looking multi-step plan. No injection patterns, no special characters. Pattern-based defenses can't detect it
- **3-layer defense reduces overall attack success by 60%** — input sanitizer (blocks injection + memory poisoning at 100%), tool permission boundary (blocks 67% of tool violations), LLM-as-judge (only layer that catches reasoning hijack)
- **Reasoning hijack only drops from 100% to 67% with full defenses** — the gap is real and fundamental to how ReAct agents work
- **Attack success correlates inversely with defender observability** — user prompt (80%), tool params (75%), conversation history (67%), tool outputs (25%), reasoning chain (100%). The least observable input has the highest attack success
- **Claude resists indirect tool injection at 25%** — the model recognizes "ignore previous instructions" patterns in tool outputs, but this may not generalize to weaker LLM backends

Methodology: LangChain + LangGraph ReAct agent, Claude Sonnet backend, 19 YAML-defined attack scenarios across 5 tested classes, 3 defense layers with measured effectiveness, temperature=0, ~$2 API cost. Cross-validated on CrewAI for prompt injection.

Repo: [github.com/rexcoleman/agent-redteam-framework](https://github.com/rexcoleman/agent-redteam-framework)

Framework is open source with the full attack taxonomy in YAML. Happy to answer questions about agent-specific attack surfaces or the defense architecture.
