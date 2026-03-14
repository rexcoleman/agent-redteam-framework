# Conference Abstract — BSides / DEF CON AI Village

## Title
Reasoning Chain Hijacking: A Novel Attack Class for Autonomous AI Agents

## Abstract (250 words)

Autonomous AI agents — systems that reason, use tools, and take actions — represent a fundamentally different attack surface than standalone LLMs. We present an open-source red-team framework that systematically discovers and demonstrates vulnerabilities in agent systems, identifying seven attack classes, five of which are not covered by OWASP LLM Top 10 or MITRE ATLAS.

Our most significant finding is **reasoning chain hijacking**, a novel attack class that exploits an agent's core capability — following structured multi-step plans — as the attack vector. By presenting attack payloads as legitimate step-by-step instructions, an attacker can direct an agent to search for sensitive data, compute on it, and exfiltrate it to persistent storage, all without triggering pattern-based defenses. This attack achieves a 100% success rate against a LangChain ReAct agent powered by Claude Sonnet.

We apply **adversarial control analysis** — classifying agent inputs by attacker controllability versus defender observability — and demonstrate that attack success correlates inversely with input observability. The reasoning chain, being internal to the agent's processing loop, is the least observable input and the most vulnerable.

We evaluate a layered defense architecture (input sanitization + tool permission boundaries) achieving 60% average attack reduction across 19 scenarios and 5 attack classes, but note that reasoning chain hijacking only decreases from 100% to 67% — identifying it as the highest-priority unsolved problem in agent security.

Framework and all attack scenarios are open source: github.com/rexcoleman/agent-redteam-framework

## Keywords
AI agents, red-teaming, prompt injection, reasoning chain hijacking, adversarial control analysis, LangChain, defense-in-depth

## Bio
Rex Coleman is an MS Computer Science student (Machine Learning) at Georgia Tech, building at the intersection of AI security and ML systems engineering. Previously 15 years in cybersecurity (FireEye/Mandiant — analytics, enterprise sales, cross-functional leadership). CFA charterholder. Creator of govML (open-source ML governance framework).
