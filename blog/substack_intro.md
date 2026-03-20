# Substack Newsletter Intro — Agent Red-Team Framework

> **Format:** Substack newsletter with personal intro, then link to full technical post
> **Subject line:** Why pattern matching can't protect your AI agents
> **Preview text:** I found an attack class with 100% success that no regex can detect

---

Hey,

I spent the last two weeks building an open-source framework for red-teaming AI agents. Not LLMs — agents. The ones that reason, use tools, and take actions.

The distinction matters because agents have a fundamentally different attack surface than models. OWASP covers prompt injection. MITRE ATLAS covers model extraction. But neither covers what happens when an agent's reasoning loop gets hijacked.

That's what I found.

**Reasoning chain hijacking** — presenting attack payloads as structured step-by-step instructions — achieved a 100% success rate against default-configured LangChain ReAct agents. Across 3 seeds. And it partially evades every defense I built.

Why? Because the attack looks exactly like a legitimate multi-step task. No injection patterns. No special characters. The agent follows the plan because following plans is what agents do.

I built a layered defense (input sanitizer + tool permission boundary) that reduces overall attacks by 60%. But reasoning hijack only drops from 100% to 67%. The only thing that catches it is a semantic defense — an LLM-as-judge that evaluates intent before execution.

The full technical write-up covers the 7-class attack taxonomy (5 classes missing from OWASP), defense architecture with measured effectiveness, and the controllability insight that predicts which inputs are most vulnerable.

Read the full post here: [link to rexcoleman.dev]

The framework is open source: [GitHub link]

If you're deploying agents in production, I'd genuinely like to hear what attack patterns you're seeing. Reply to this email or find me on LinkedIn.

— Rex

