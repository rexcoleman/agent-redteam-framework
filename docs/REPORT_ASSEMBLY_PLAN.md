# REPORT ASSEMBLY PLAN

<!-- version: 1.0 -->
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
- See [FIGURES_TABLES_CONTRACT](../core/FIGURES_TABLES_CONTRACT.tmpl.md) §3-4 for figure/table definitions and acceptance criteria
- See [METRICS_CONTRACT](../core/METRICS_CONTRACT.tmpl.md) §8 for summary table interface and required columns

**Downstream (depends on this contract):**
- See [PRE_SUBMISSION_CHECKLIST](PRE_SUBMISSION_CHECKLIST.tmpl.md) §3 for report content audit

Adversarial ML on Network Intrusion Detection — Report Assembly Plan

---

## 1) Purpose & Report Constraints

This document provides the plan for assembling the final report. Every decision traces to the authority hierarchy.

**Hard constraints:**

| Constraint | Source | Penalty |
|---|---|---|
| Max {{PAGE_LIMIT}} pages (including figures + references) | *(cite)* | Content past limit not reviewed |
| Written in {{FORMAT}} on {{PLATFORM}} | *(cite)* | Required format |
| READ-ONLY link in report or delivery | *(cite)* | Non-compliance |
| Paragraph prose; analysis MUST NOT be bullet lists | *(cite)* | Non-compliance |
| Two deliverables: Report + REPRO | *(cite)* | Incomplete delivery |
| At least {{MIN_REFS}} peer-reviewed references | *(cite)* | Non-compliant |
| AI Use Statement | *(cite)* | Non-compliant |
| Single citation style | *(cite)* | Non-compliance |

---

## 2) Section Outline & Page Budget

| Section | Content | Budget |
|---|---|---|
| Title / Abstract | Title, authors, optional abstract (~150 words) | 0.25 |
| 1. Introduction | Problem, gap, what report does | 0.50 |
| 2. Data & EDA | Datasets, metrics, preprocessing, EDA summary | 0.50 |
| 3. Hypotheses | One per dataset, before experiments | 0.30 |
| 4. Methods | Splits, budgets, seeds, hardware, architecture | 0.75 |
| 5-N. Results | One section per experimental part | *(allocate)* |
| Conclusion | Accept/reject hypotheses, decision rule, limitations | 0.50 |
| AI Use Statement | Per template | 0.10 |
| References | Peer-reviewed sources | 0.40 |
| | **Total** | **~{{TOTAL}}** |

*(The margin accommodates figures, tables, and float placement.)*

---

## 3) Writing Rules

### Results Sections (CRITICAL)

- MUST be paragraph prose with coherent reasoning
- Every figure/table reference MUST include a takeaway
- Results structured around testing hypotheses, not merely reporting
- **CCC paragraph structure:** Context (what question) → Content (evidence) → Conclusion (what it means)
- Logical thread: each section opens by connecting to the previous section's key finding

### Hypotheses

- Written as prose paragraphs
- Stated before experiments (not retroactive)
- Include: prediction, reasoning from EDA, optimization/ML mechanism, baseline prediction

### Methods

- Bullets acceptable for hyperparameter lists and protocol steps
- Rationale for design choices in prose

### Central Contribution (Rule of One)

Before writing, identify the single most important finding that ties all parts together. Craft the title to convey this finding. Every section should advance this central thread.

---

## 4) Figure & Table Placement

*(Map each figure/table to its report section and interpretation goal.)*

| ID | Title | Section | What to Interpret |
|----|-------|---------|-------------------|
| F1 | *(title)* | *(section)* | *(interpretation goal)* |
| T1 | Summary Table | Before Conclusion | Side-by-side comparison of all methods |
| *(add rows)* | | | |

---

## 5) Baseline Comparison Requirement

Every intervention MUST be explicitly compared to the baseline, stating improved / not improved / conditionally improved.

**Template:**

> Compared to the baseline ({{BASELINE_METRIC_NAME}} = {{BASELINE_VALUE}}), [method] achieved a median {{METRIC}} of Y.YYY (IQR: [a, b]) under [budget], representing a [+/-]Z.ZZZ absolute change. This [improvement / non-improvement] is [attributable to / explained by] [mechanism].

---

## 6) Hypothesis Templates

### Statement (Section 3)

> **Hypothesis ({{DATASET}}):** Based on [EDA observation], I predict that [specific behavior], because [mechanism]. Relative to the baseline ({{METRIC}} = X.XXX), I predict that [intervention] will [improve / not improve] because [reasoning].

### Resolution (Conclusion)

> **Resolution ({{DATASET}}):** The hypothesis predicted [summary]. Experiments showed [observed result: median = Y.YYY, IQR = [a, b], under Z evals]. [Accept / Reject]: the prediction was [supported / contradicted] because [quantitative evidence]. The compute cost was [budget], suggesting [practical implication].

---

## 7) References Plan

At least {{MIN_REFS}} peer-reviewed references, used substantively (not just listed).

| Category | Purpose | Example Topics |
|---|---|---|
| *(e.g.)* Optimizer theory | Justify ablation design | Adam, AdamW |
| *(e.g.)* Regularization | Justify technique selection | Dropout, label smoothing |
| *(e.g.)* Evaluation metrics | Justify metric choices | F1 for imbalanced data |
| *(add rows)* | | |

**Rules:**
- Do NOT fabricate citations
- Every source MUST be used substantively in report text
- One consistent citation style throughout

---

## 8) REPRO Document Checklist

The REPRO document MUST contain:

- [ ] READ-ONLY link to report
- [ ] Git commit SHA from final push
- [ ] Exact run commands for all scripts
- [ ] Environment setup commands
- [ ] Data paths and acquisition instructions
- [ ] Random seeds (default + stability list)
- [ ] EDA summary confirmation per dataset
- [ ] Output directory structure

---

## 9) Pre-Flight Checklist

### Report Content

- [ ] **CRITICAL:** Page count within limit
- [ ] **CRITICAL:** Paragraph prose in results/discussion
- [ ] **CRITICAL:** READ-ONLY link present
- [ ] AI Use Statement present
- [ ] Sufficient peer-reviewed references
- [ ] Consistent citation style
- [ ] Hypotheses stated before experiments
- [ ] Hypotheses resolved with quantitative evidence

### Figures & Tables

- [ ] **CRITICAL:** All required figures present
- [ ] **CRITICAL:** All required tables present
- [ ] Every figure/table referenced with interpretation
- [ ] Summary table has required columns + baseline row
- [ ] Captions include takeaways

### Evaluation Discipline

- [ ] **CRITICAL:** Dispersion shown (not just means)
- [ ] **CRITICAL:** Budgets matched across compared methods
- [ ] **CRITICAL:** Test set used exactly once
- [ ] Generalization gap reported
- [ ] Sanity checks reported
- [ ] Failures explained

### Baseline & Decision

- [ ] **CRITICAL:** Baseline comparison per dataset
- [ ] Decision rule / practical recommendation in conclusion

### Delivery

- [ ] Two deliverables (Report + REPRO)
- [ ] Code pushed to designated repository
- [ ] Commit SHA matches REPRO
- [ ] Delivered by delivery date
