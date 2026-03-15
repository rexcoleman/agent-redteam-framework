# PUBLICATION PIPELINE — Agent Security Red-Team Framework

<!-- version: 2.0 -->
<!-- created: 2026-03-14 -->
<!-- last_validated_against: FP-02 FINDINGS.md -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `docs/PROJECT_BRIEF.md` | Primary spec — highest authority |
> | Tier 2 | — | No external FAQ |
> | Tier 3 | `docs/ADVERSARIAL_EVALUATION.md` | Advisory — adversarial methodology |
> | Contract | This document | Implementation detail — subordinate to all tiers above |

---

## 1) Target Venue

- [x] Blog (canonical home — Hugo site)
- [x] Conference CFP: BSides / DEF CON AI Village
- [ ] LinkedIn article (long-form)

**Conference deadline:** Check BSides 2026 CFP schedule (typically 2-3 months before event)

---

## 2) Content Identity

| Property | Value |
|----------|-------|
| **Working title** | I Red-Teamed AI Agents: Here's How They Break (and How to Fix Them) |
| **Content pillar** | AI Security Architecture (40% pillar) |
| **Target audience** | P1: Security engineers building with AI agents. P2: Engineering managers evaluating agent safety. P3: AI security hiring managers (brand signal). |
| **One-line thesis** | Reasoning chain hijacking — an attack pattern where structured step-by-step instructions exploit an agent's core capability — achieves 100% success rate against default-configured agents and partially evades all current defenses. |
| **What was shipped** | github.com/rexcoleman/agent-redteam-framework — open-source red-team framework with 7 attack classes, 19 scenarios, and layered defense architecture |

### Voice Check

| Test | Pass? |
|------|-------|
| References something you built (not theoretical) | [x] Framework with working attack scripts |
| Shows work (code, architecture, data) not just opinions | [x] 19 scenarios, success rates, defense measurements |
| Avoids "5 Tips" / "Why You Should" / "The Future of" framing | [x] "Here's How They Break" = showing work |
| Includes at least one architecture diagram | [x] Defense-in-depth layered architecture |
| Links to a GitHub repo with working code | [x] agent-redteam-framework |

---

## 3) Draft Structure

| # | Section | Content | Estimated Length | Status |
|---|---------|---------|-----------------|--------|
| 1 | Hook | "I sent 19 attack scenarios at a LangChain agent. 13 succeeded." | 2-3 sentences | Draft |
| 2 | Context | Built open-source framework, tested against LangChain ReAct + Claude | 1 paragraph | Draft |
| 3 | Architecture | Defense-in-depth diagram (input sanitizer → tool boundary → agent) + controllability matrix | 2 paragraphs + diagram | Draft |
| 4 | Key Findings | (a) Reasoning hijack 100%, (b) Tool boundary 75%, (c) Layered defense 60% reduction, (d) Indirect injection fails on Claude | 4 subsections | Draft |
| 5 | Code Examples | Attack scenario YAML, reasoning hijack payload, defense wrapper | 3 code blocks | Draft |
| 6 | What I Learned | Controllability analysis transfers across domains (3rd validation). Pattern-based defenses can't stop reasoning hijack. | 2 paragraphs | Draft |
| 7 | Conclusion + Links | Repo link, govML link, call for contributions | 1 paragraph | Draft |

### Architecture Diagram

Defense-in-depth layered architecture showing:
- User input → Input Sanitizer (Layer 1) → Tool Permission Boundary (Layer 2) → Agent
- Controllability matrix overlay: which inputs each layer can observe
- Gap annotation: reasoning chain = unobservable by both layers

---

## 4) Evidence Inventory

| Claim | Evidence | Source |
|-------|---------|-------|
| 7 attack classes systematized, 5 not covered by OWASP/ATLAS (reasoning chain hijacking = strongest novelty claim) | Taxonomy document | `docs/attack_taxonomy.md` |
| Reasoning chain hijacking: 100% success | 3/3 scenarios succeeded | `outputs/attacks/langchain_react_all_seed42/summary.json` |
| Prompt injection: 80% success | 4/5 scenarios | Same |
| Tool boundary violation: 75% success | 3/4 scenarios | Same |
| Memory poisoning: 67% success | 2/3 scenarios | Same |
| Indirect injection: 25% (Claude resists) | 1/4 scenarios | Same |
| Layered defense: 60% average reduction | Comparison table | `outputs/defenses/langchain_react_layered_seed42/summary.json` |
| Prompt injection fully blocked by sanitizer | 80% → 0% | Same |
| Cross-domain controllability validation | 3 domains (IDS, CVE, agents) | FINDINGS.md §RQ3 |
| Total API cost ~$2 | Token tracking | FINDINGS.md §Cost |

---

## 5) Distribution Checklist

### 5.1 Pre-Publication

- [x] Draft reviewed for builder voice (§2 voice check passes)
- [ ] Architecture diagram finalized and embedded
- [ ] Code examples tested and runnable
- [x] All claims traceable to evidence inventory (§4)
- [ ] Links to repo and govML included
- [ ] No anti-claims present (grep for "superior", "prove", "novel", "always", "never", "best")

### 5.2 Publish

- [ ] Published on Hugo site (canonical URL: `https://rexcoleman.dev/posts/agent-redteam/`)
- [ ] Emailed via Substack (with email-specific intro paragraph)
- [ ] Canonical URL set in Substack post metadata

### 5.3 Cross-Post (within 24 hours)

- [ ] Cross-posted to dev.to with canonical URL
- [ ] Cross-posted to Hashnode with canonical URL
- [ ] LinkedIn native text post (key insight + 3-5 bullets)
- [ ] Blog link added as first comment on LinkedIn post
- [ ] Mastodon (infosec.exchange) post with link

### 5.4 Post-Publication (within 48 hours)

- [ ] Submitted to Hacker News (strong technical post — YES)
- [ ] Respond to comments on all platforms
- [ ] Update govML LESSONS_LEARNED.md with publishing friction

---

## 6) Metrics to Track

| Metric | Source | Check After |
|--------|--------|-------------|
| Blog page views | Cloudflare / Plausible | 7 days |
| Substack open rate | Substack dashboard | 3 days |
| LinkedIn impressions | LinkedIn analytics | 7 days |
| dev.to / Hashnode views | Platform dashboards | 7 days |
| GitHub repo traffic spike | GitHub Insights | 7 days |
| Hacker News points | HN | 24 hours |
| BSides CFP acceptance | Email | 30 days |
