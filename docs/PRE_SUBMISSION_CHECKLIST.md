# PRE-SUBMISSION CHECKLIST

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
- See [REPORT_ASSEMBLY_PLAN](REPORT_ASSEMBLY_PLAN.tmpl.md) §9 for pre-flight checklist definitions
- See [ENVIRONMENT_CONTRACT](../core/ENVIRONMENT_CONTRACT.tmpl.md) §5 for environment reproducibility checks
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §5 for integrity verification commands
- See [SCRIPT_ENTRYPOINTS_SPEC](../core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §7 for test suite requirements

**Downstream (depends on this contract):**
- None — this is the final delivery audit.

Adversarial ML on Network Intrusion Detection — Attribution, Compliance & Delivery Readiness Audit

---

## Purpose

This checklist ensures that the delivered repository and report are compliant with attribution and IP policies, contain no prohibited artifacts, and are fully reproducible. Run this checklist before every delivery.

*Adapt this section to your organization's IP/attribution policy. In academic contexts, this maps to academic honesty requirements; in industry, to IP compliance and contractual obligations.*

---

## 1) Repository Hygiene

### Files That MUST NOT Be in the Repo

- [ ] **Source materials** — Requirements documents, FAQs, evaluation criteria, specification documents provided by the project sponsor
- [ ] **Internal scaffolding** — Implementation playbooks, task boards, risk registers, decision logs, changelogs (unless required by the project specification)
- [ ] **Audit reports** — Any compliance audit documents
- [ ] **Draft/scratch files** — Hypothesis drafts, notes, TODO lists
- [ ] **Raw data** — Large data files should be gitignored, not committed
- [ ] **Compiled files** — `.pyc`, `__pycache__/`, `.ipynb_checkpoints/`
- [ ] **IDE files** — `.vscode/`, `.idea/`, `.DS_Store`
- [ ] **Credentials** — `.env`, API keys, tokens

### Verification Commands

```bash
# Check for source materials (adapt patterns to your project)
git ls-files | grep -iE "(assignment|rubric|faq|spec_requirements|honesty)" | head -20

# Check for compiled files
git ls-files | grep -E "\\.pyc$|__pycache__" | head -20

# Check for large files
git ls-files | xargs ls -la 2>/dev/null | awk '$5 > 1000000 {print $5, $NF}' | sort -rn | head -10

# Check for sensitive files
git ls-files | grep -iE "(\\.env|credentials|secret|token)" | head -10
```

---

## 2) Git History Audit

### Raw Data in History

Even if raw data files are currently gitignored, they may exist in old commits.

```bash
# Check for data files in git history
git rev-list --objects --all | grep -iE "\\.(csv|tsv|json|npz|pkl|parquet)$" | head -20

# Check for large blobs in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize) %(objectname) %(rest)' | awk '$1 == "blob" && $2 > 1000000 {print $2, $4}' | sort -rn | head -10
```

**If found:** Consider an orphan branch strategy to create a clean single-commit history:

```bash
git checkout --orphan clean-main
git rm -r --cached .
git add -A
git commit -m "Clean delivery commit"
git branch -D main
git branch -m clean-main main
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## 3) Report Content Audit

- [ ] **Report link** — Valid READ-ONLY link (not a placeholder like `XXXX-REPLACE-ME`)
- [ ] **Git SHA** — Matches the actual final commit pushed to the designated repository
- [ ] **AI Use Statement** — Present, accurate, placed before References
- [ ] **Test count** — If mentioned (e.g., "294 tests pass"), verify it matches `pytest` output
- [ ] **Dataset statistics** — Row counts, feature counts, class distributions match actual data
- [ ] **Metric values** — All reported numbers trace to `final_eval_results.json`
- [ ] **No internal references** — Report doesn't reference internal docs (playbooks, task boards, etc.)
- [ ] **Special characters** — No unescaped `#` in LaTeX URLs, no Unicode in LaTeX that your editor can't compile

---

## 4) Reproducibility Verification

- [ ] **Environment installs cleanly:** `conda env create -f environment.yml` exits 0
- [ ] **All scripts exist:** Every command in REPRO document references an existing script
- [ ] **Tests pass:** `python -m pytest tests/ -v` — all pass
- [ ] **Seeds documented:** Default seed and stability list in REPRO
- [ ] **Data paths documented:** REPRO explains where to get data and where to place it

---

## 5) Designated Repository Check

- [ ] **Correct repo:** Code is on the designated repository (not a personal fork)
- [ ] **Correct branch:** Main/master branch has the delivery code
- [ ] **Commit SHA matches:** REPRO document SHA matches the actual pushed commit
- [ ] **No extra commits after SHA:** If REPRO references a specific SHA, no subsequent commits change the code

*In academic contexts, this maps to your institution's required repository. In industry, this maps to your organization's source control system.*

---

## 6) Attribution & IP Compliance

*Adapt to your organization's attribution policy.*

- [ ] **No prior-engagement materials:** No code, reports, or artifacts from prior engagements that are not properly attributed
- [ ] **No unauthorized collaboration artifacts:** No shared code from collaborators (unless permitted)
- [ ] **AI disclosure:** All AI-assisted work properly disclosed per policy
- [ ] **Citations:** All external references properly cited
- [ ] **Original work:** Analysis and interpretation are original, not copied

---

## 7) Final Delivery Checklist

| Item | Status | Notes |
|------|--------|-------|
| Report PDF within page limit | [ ] | |
| REPRO PDF complete | [ ] | |
| Code pushed to designated repository | [ ] | |
| SHA in REPRO matches push | [ ] | |
| READ-ONLY link works in incognito | [ ] | |
| Delivery platform uploaded | [ ] | |
| By delivery date | [ ] | |
