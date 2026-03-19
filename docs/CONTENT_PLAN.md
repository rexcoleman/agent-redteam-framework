# Content Plan — Agent Security Red-Team Framework (FP-02)

> **Purpose:** Links experiment completion to content production. Required by R27 (Content Trigger Rule) and Gate 9 (V-Cluster Gate).
> **Deadline:** 14 days after project reaches COMPLETE status.
> **govML version:** v3.0

---

## 1. Planned Content Artifacts

| Format | Title (working) | Target Date | Audience Side | Status |
|--------|----------------|-------------|---------------|--------|
| Technical Blog Post | I Red-Teamed AI Agents: Here's How They Break (and How to Fix Them) | 2026-03-26 | Security OF AI | DRAFTED |
| Conference Abstract | Reasoning Chain Hijacking: A Novel Attack Class for Autonomous AI Agents | 2026-04-01 | Security OF AI | DRAFTED |
| LinkedIn Post | 100% success rate against default AI agents — reasoning chain hijacking | 2026-03-26 | Both | NOT STARTED |
| Substack Newsletter | Why pattern matching can't protect your AI agents | 2026-03-26 | Security OF AI | NOT STARTED |
| Reddit r/netsec | Self-post: 5 agent attack classes OWASP doesn't cover | 2026-03-28 | Security OF AI | NOT STARTED |

### TIL Posts (quick signals from this research)

| # | Title | Key Number | Status |
|---|-------|-----------|--------|
| 1 | $2 to red-team an AI agent end-to-end | $2 total API cost | NOT STARTED |
| 2 | Claude resists indirect injection at the model level (25% success) | 25% indirect injection rate | NOT STARTED |
| 3 | Tool boundary defense alone = 0% reduction (only works layered) | 0% standalone reduction | NOT STARTED |

---

## 2. Key Findings for Content (from FINDINGS.md)

| # | Finding | Claim Tag | Blog Hook |
|---|---------|-----------|-----------|
| 1 | Reasoning chain hijacking achieves 100% success against default agents | [DEMONSTRATED] | "The most dangerous attack looks like a legitimate task" |
| 2 | 5 of 7 attack classes target surfaces not covered by OWASP/ATLAS | [DEMONSTRATED] | "Existing frameworks miss the agent attack surface" |
| 3 | Layered defense achieves 60% attack reduction; reasoning hijack only 33% | [DEMONSTRATED] | "The gap that no pattern-based defense can close" |
| 4 | Attack success correlates inversely with defender observability | [DEMONSTRATED] | "Controllability analysis is a general security principle" |
| 5 | Full 3-layer defense (with LLM judge) reduces reasoning hijack to 33% | [DEMONSTRATED] | "Semantic defense is the only thing that catches it" |

---

## 3. Figures for Blog (from make_report_figures.py)

| Figure File | Description | Blog Use | Copied to blog/images/? |
|------------|-------------|----------|------------------------|
| attack_success_rates.png | Per-class attack success with error bars | Key finding visualization | YES |
| defense_comparison.png | 4-layer defense stack comparison | Defense architecture | YES |
| controllability_analysis.png | Observability vs attack success | Architectural insight | YES |
| defense_effectiveness.png | Defense reduction by class | Supplemental | YES |
| attack_by_class.png | Attack heatmap | Supplemental | YES |

---

## 4. Distribution Plan

| Channel | Format | Adaptation Notes | Status |
|---------|--------|-----------------|--------|
| rexcoleman.dev | Blog post (Primary) | Full technical post with figures | NOT STARTED |
| Substack | Newsletter (personal intro + link) | Personal angle: why I built this | NOT STARTED |
| LinkedIn | Native post (3-5 bullet summary, link in comment) | Hook: 100% success rate, builder-in-public | NOT STARTED |
| Reddit r/netsec | Self-post (500w technical summary) | Focus on novel attack class, link to framework | NOT STARTED |
| HN | Link submission (specific title) | Title: "Reasoning Chain Hijacking: 100% success against default AI agents" | NOT STARTED |
| dev.to | Cross-post (canonical URL) | Full post, canonical to rexcoleman.dev | NOT STARTED |
| BSides/DEF CON AI Village | CFP abstract | 250-word abstract drafted in blog/conference_abstract.md | DRAFTED |

---

## 5. Audience Side Check

- [x] Security OF AI (builders deploying AI systems)
- [ ] Security FROM AI (defenders facing AI-powered threats)
- [ ] Both

Primary audience: developers and security engineers deploying autonomous AI agents in production. Secondary: CISOs evaluating agent risk.

---

## 6. Gate 9 Checklist (V-Cluster Gate)

- [ ] Blog post published on rexcoleman.dev
- [ ] Post passes R25 (format minimums)
- [ ] Post passes R26 (image gate: >=1 inline figure)
- [ ] Post distributed to >=2 channels (R21)
- [ ] Forward reference to/from >=1 other post
- [ ] `format:` tag in Hugo front matter
