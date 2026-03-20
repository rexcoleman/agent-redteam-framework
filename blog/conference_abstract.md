# Conference Abstract — BSides / DEF CON AI Village

## Title
Reasoning Chain Hijacking: A Novel Attack Class for Autonomous AI Agents

## Abstract (250 words)

Autonomous AI agents — systems that reason, use tools, and take actions — represent a fundamentally different attack surface than standalone LLMs. Five of the seven attack classes we systematize target agent-specific surfaces not covered by OWASP LLM Top 10 or MITRE ATLAS, and the most dangerous exploits the agent's core capability as the attack vector.

We present an open-source red-team framework and its key finding: reasoning chain hijacking — presenting attack payloads as structured step-by-step instructions — achieves 100% success against default-configured LangChain ReAct agents (Claude 3.5 Sonnet, 3 seeds, temperature=0). The attack works because following plans is what agents do. Adversarial control analysis shows attack success correlates inversely with input observability; the reasoning chain is the least observable input and the most vulnerable. A layered defense (input sanitization + tool permission boundaries) reduces overall attacks by 60%, but reasoning hijack only drops from 100% to 67%.

Attendees will leave with a 7-class agent attack taxonomy, a controllability framework for prioritizing agent defenses by observability, and access to the open-source framework for red-teaming their own agent deployments. Suitable for intermediate to advanced practitioners building or securing agent systems.

## Keywords
AI agents, red-teaming, prompt injection, reasoning chain hijacking, adversarial control analysis, LangChain, defense-in-depth

## Bio
Rex Coleman is an MS Computer Science student (Machine Learning) at Georgia Tech, building at the intersection of AI security and ML systems engineering. Previously 15 years in cybersecurity (FireEye/Mandiant — analytics, enterprise sales, cross-functional leadership). CFA charterholder. Creator of govML (open-source ML governance framework).
