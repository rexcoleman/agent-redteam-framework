# Rubric & FAQ Traceability Matrix

> **Template version:** 1.0
> **Authority:** Tier 2 (Assignment Compliance)
> **Enforcement phases:** Phase 4 (Report Draft), Phase 5 (Pre-Submission)
> **Cross-references:** REPORT_CONSISTENCY_SPEC, REPORT_ASSEMBLY_PLAN, PRE_SUBMISSION_CHECKLIST

---

## Purpose

This template maps every rubric item and FAQ question to a specific report location, ensuring 100% coverage before submission. From RL report experience: 8 rubric/FAQ gaps were found across 4 separate audit cycles (AC7-AC9) — this matrix eliminates that pattern by making gaps visible upfront.

---

## How to Use

1. **Phase 0 (Setup):** Extract all rubric items from assignment spec and all FAQ questions. Fill the tables below.
2. **Phase 4 (Report Draft):** After completing the draft, fill the "Report Section" and "Paragraph" columns.
3. **Phase 5 (Pre-Submission):** Run `scripts/check_rubric.py` to verify all items are ADDRESSED. Fix any GAPs before submission.

---

## Rubric Items

**Source:** `{{RUBRIC_SOURCE_PATH}}` (e.g., `requirements/assignment_spec.md`)

| # | Category | Requirement | Report Section | Paragraph/Location | Status | Evidence | Verified Date |
|---|----------|-------------|---------------|-------------------|--------|----------|---------------|
| R-01 | {{CATEGORY}} | {{REQUIREMENT_TEXT}} | {{SECTION}} | {{PARA_OR_LINE}} | {{ADDRESSED/GAP/PARTIAL}} | {{QUOTE_OR_REF}} | {{DATE}} |

### Status Definitions
- **ADDRESSED**: Requirement explicitly covered in the indicated location
- **PARTIAL**: Requirement mentioned but not fully addressed (needs expansion)
- **GAP**: Requirement not found anywhere in the report (MUST fix before submission)
- **N/A**: Requirement does not apply to this project (document rationale)

---

## FAQ Items

**Source:** `{{FAQ_SOURCE_PATH}}` (e.g., `requirements/assignment_FAQ.md`)

| # | Question | Report Section | Paragraph/Location | Status | Evidence | Verified Date |
|---|----------|---------------|-------------------|--------|----------|---------------|
| FAQ-01 | {{FAQ_QUESTION}} | {{SECTION}} | {{PARA_OR_LINE}} | {{ADDRESSED/GAP/PARTIAL}} | {{QUOTE_OR_REF}} | {{DATE}} |

---

## Extra Credit Items (Optional)

| # | EC Requirement | Report Section | Paragraph/Location | Status | Evidence | Verified Date |
|---|---------------|---------------|-------------------|--------|----------|---------------|
| EC-01 | {{EC_REQUIREMENT}} | {{SECTION}} | {{PARA_OR_LINE}} | {{ADDRESSED/GAP/PARTIAL}} | {{QUOTE_OR_REF}} | {{DATE}} |

---

## Coverage Summary

```
Rubric:  {{ADDRESSED_COUNT}}/{{TOTAL_RUBRIC}} ADDRESSED ({{RUBRIC_PERCENT}}%)
FAQ:     {{ADDRESSED_COUNT}}/{{TOTAL_FAQ}} ADDRESSED ({{FAQ_PERCENT}}%)
EC:      {{ADDRESSED_COUNT}}/{{TOTAL_EC}} ADDRESSED ({{EC_PERCENT}}%)

GAP items requiring attention:
{{GAP_ITEM_LIST}}

PARTIAL items requiring expansion:
{{PARTIAL_ITEM_LIST}}
```

---

## Gate Criteria

- **Phase 4 gate:** ≥80% rubric items ADDRESSED, 0 CRITICAL rubric items as GAP
- **Phase 5 gate (submission):** 100% rubric items ADDRESSED or N/A, 100% FAQ items ADDRESSED or N/A
- **Fail action:** Do not submit until all GAP items resolved

---

## Common Gap Patterns (from UL/RL experience)

These are the rubric/FAQ categories most frequently found as gaps in prior projects. Pay special attention:

1. **Distance/similarity metric justification** — Why this metric for this data?
2. **Hyperparameter search ranges and sensitivity** — What ranges were searched? Why?
3. **Initialization choices** — Q_0, random seeds, starting conditions
4. **Convergence criteria** — How do you know the algorithm converged?
5. **Reward/objective function details** — Exact formulation and justification
6. **Environment/MDP motivation** — Why this environment for this research question?
7. **Ablation analysis** — What happens when you remove components?
8. **Function approximation challenges** — Specific to deep/neural methods
9. **Noise sensitivity** — How do results change with noise?
10. **Suggested improvements** — What would you do differently?

---

## Audit History

| Date | Auditor | Rubric Coverage | FAQ Coverage | GAPs Found | GAPs Resolved |
|------|---------|----------------|-------------|------------|---------------|
| {{DATE}} | {{AUDITOR}} | {{PERCENT}} | {{PERCENT}} | {{COUNT}} | {{COUNT}} |

---

## Appendix: Research Question Traceability (Optional)

> **Activation:** Include this appendix for self-directed projects (parallel projects, portfolio
> pieces, independent research) that have no external rubric or FAQ. Replace the Rubric Items
> and FAQ Items sections above with this section. Delete if using the standard rubric tables.

For self-directed projects, traceability maps research questions (not rubric items) to report sections.

### Research Questions

| # | Research Question | Report Section | Paragraph/Location | Status | Evidence |
|---|-------------------|---------------|-------------------|--------|----------|
| RQ-01 | {{RESEARCH_QUESTION}} | {{SECTION}} | {{PARA_OR_LINE}} | {{ADDRESSED/GAP/PARTIAL}} | {{QUOTE_OR_REF}} |

### Claims Traceability

Every claim in the report MUST trace to specific evidence:

| # | Claim | Evidence Type | Evidence Location | Verified |
|---|-------|--------------|-------------------|----------|
| CL-01 | {{CLAIM_TEXT}} | {{figure/table/metric/log}} | {{PATH_OR_REF}} | {{YES/NO}} |

### Self-Directed Gate Criteria

- **Draft gate:** Every RQ has at least one ADDRESSED section; every claim has evidence
- **Publication gate:** 100% RQ coverage; zero unsupported claims; TRADEOFF_LOG.md complete
- **Fail action:** Do not publish until all GAPs resolved and all claims verified
