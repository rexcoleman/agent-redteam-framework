# IMPLEMENTATION PLAYBOOK

<!-- version: 2.0 -->
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
- See [ENVIRONMENT_CONTRACT](../core/ENVIRONMENT_CONTRACT.tmpl.md) §5 for setup commands (Phase 0)
- See [DATA_CONTRACT](../core/DATA_CONTRACT.tmpl.md) §8 for data acceptance tests (Phase 1)
- See [METRICS_CONTRACT](../core/METRICS_CONTRACT.tmpl.md) §7 for sanity check requirements (Phase 3)
- See [EXPERIMENT_CONTRACT](../core/EXPERIMENT_CONTRACT.tmpl.md) §exit gates for per-part exit criteria
- See [FIGURES_TABLES_CONTRACT](../core/FIGURES_TABLES_CONTRACT.tmpl.md) §7 for artifact acceptance criteria
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §8 for manifest verification gate
- See [SCRIPT_ENTRYPOINTS_SPEC](../core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §6 for reproduction sequence

**Downstream (depends on this contract):**
- See [TASK_BOARD](TASK_BOARD.tmpl.md) for operational task tracking derived from phase plan
- See [RISK_REGISTER](RISK_REGISTER.tmpl.md) for phase-gate risk scanning

Adversarial ML on Network Intrusion Detection — Execution Playbook

---

## 0) Purpose

This playbook is the single operational document for implementing the **Adversarial ML on Network Intrusion Detection** project end-to-end. It translates all tiered requirements and project contracts into a concrete iteration loop with phase gates, commands, and stop-ship checks.

**Scope:** Code implementation, experiment execution, artifact generation, and report assembly. This playbook does NOT replace any contract; it orchestrates them.

---

## 1) Conflict Resolution Rules

1. **T1 vs anything:** T1 wins. No exceptions.
2. **T2 vs T3 or contracts:** T2 wins.
3. **T3 vs contracts:** T3 is advisory. If T3 contradicts a contract, check whether the contract is grounded in T1/T2. If yes, the contract stands.
4. **Contract vs contract:** Resolve by tracing both to T1/T2. The one with stronger grounding wins. If ambiguous, record in DECISION_LOG and pick the conservative interpretation.
5. **Silence:** If T1/T2 are silent, contracts may specify choices using SHOULD (not MUST).

### MUST vs SHOULD Convention

- **MUST** = backed by explicit T1/T2 requirement or a contract clause directly implementing one
- **SHOULD** = project-level hardening or best practice not explicitly mandated by T1/T2

---

## 2) Phase Plan with DoD Gates

Each phase has a hard gate. No work in phase N+1 may begin until phase N's gate passes.

### Phase 0 — Environment & Governance Lock

**Goal:** Infrastructure ready, budgets locked, splits frozen, prior work integrated.

| # | Step | Command / Action | DoD | Verification |
|---|------|-----------------|-----|-------------|
| 0.1 | Create environment | `conda env create -f environment.yml` | Exits 0; env active | `conda env list \| grep adversarial-ids` |
| 0.2 | Verify environment | `bash scripts/verify_env.sh` | Exits 0; versions printed | Script prints Python + all key library versions |
| 0.3 | Vendor prior work *(if applicable)* | See [PRIOR_WORK_REUSE](PRIOR_WORK_REUSE.tmpl.md) §8 | Provenance record written; hashes verified | `python scripts/verify_{{PRIOR_PROJECT}}_snapshot.py` exits 0 |
| 0.4 | Convert/verify data splits | `python scripts/check_data_ready.py` | Exits 0; split files in `data/splits/` | SHA-256 hashes match provenance record |
| 0.5 | Populate budgets | Fill all keys in `{{BUDGET_CONFIG}}` | All keys non-null | Assert cross-part budget constraints (e.g., `part3.grad_evals == part2.grad_evals`) |
| 0.6 | Lock baseline metrics | Populate `{{BASELINE_CONFIG}}` | Contains baseline test metrics per dataset | File committed alongside budgets |
| 0.7 | Run config schema validation | `python scripts/validate_config.py` *(if available)* | Exits 0; all required keys present | Required keys per EXPERIMENT_CONTRACT §2 |
| 0.8 | Commit governance | `git commit -m "CONTRACT_CHANGE: Phase 0 lock"` | All contracts + configs committed | `git diff --cached` shows expected files |

**Gate Definition of Done:**
- [ ] Environment creates and activates without errors
- [ ] `verify_env.sh` exits 0
- [ ] Prior work snapshot verified *(if applicable)*
- [ ] Data splits present with recorded hashes
- [ ] Budget config fully populated; cross-part constraints satisfied
- [ ] Baseline metrics config present
- [ ] Git remote configured and test push succeeds
- [ ] All files committed as `CONTRACT_CHANGE`
- [ ] CHANGELOG entry recorded
- [ ] **All tradeoff decisions from this phase logged in DECISION_LOG.md** (ADR format: context, decision, consequences, contracts affected)

**Integration hooks:**
- RISK_REGISTER: Verify all Phase 0 risks (R-A1, R-A2, R-A3, R-C2, R-H*) are addressed
- DECISION_LOG: Record any ADRs for ambiguities resolved during setup — **this is mandatory, not optional**
- TASK_BOARD: Mark all Phase 0 tasks as Done

---

### Phase 1 — Data Readiness & Validation

**Goal:** Data verified, leakage prevented, EDA complete.

| # | Step | Command | DoD |
|---|------|---------|-----|
| 1.1 | Verify raw data | `python scripts/check_data_ready.py` | Exits 0; raw files present with correct hashes |
| 1.2 | Run leakage tripwires | `python scripts/check_leakage.py` | Exits 0; LT-1, LT-2, LT-3 all pass |
| 1.3 | Run EDA | `python scripts/run_eda.py --dataset {{DATASET}} --seed {{DEFAULT_SEED}}` | Exits 0; EDA summaries written |
| 1.4 | Save initial weights | *(Implemented in training scripts)* | `state_dict` saved per seed |

**Gate Definition of Done:**
- [ ] `check_data_ready.py` exits 0
- [ ] `check_leakage.py` exits 0
- [ ] EDA summaries exist for all datasets
- [ ] Initial weights saved
- [ ] **All tradeoff decisions from this phase logged in DECISION_LOG.md**

**Integration hooks:**
- RISK_REGISTER: Verify R-A1 through R-A5 addressed
- DECISION_LOG: Record any data preprocessing or split decisions
- TASK_BOARD: Mark Phase 1 tasks Done

---

### Phase 2 — Hypotheses

**Goal:** Testable hypotheses written before experiments.

| Step | Action | DoD |
|------|--------|-----|
| Formulate hypotheses | Write grounded in EDA + theory | Each includes: predicted behavior, reasoning, mechanism, baseline prediction |

**Gate:** Hypotheses committed. Experiments MUST NOT run before this.

---

### Phase 3 — Sanity Checks

**Goal:** Pipeline credibility established.

| Step | Command | DoD |
|------|---------|-----|
| Run sanity checks | `python scripts/run_sanity_checks.py` | Exits 0; results in `outputs/sanity_checks/` |
| Verify results | Inspect outputs | Dummy ≈ majority proportion; shuffled ≈ chance |

**Gate:** Sanity checks pass.

---

### Phase 4-N — Experiments

*(Create one phase per experimental part. Template:)*

### Phase {{N}} — {{PART_NAME}}

**Goal:** *(One-sentence goal)*

| # | Step | Command | DoD |
|---|------|---------|-----|
| {{N}}.1 | Run experiments | `python scripts/run_{{PART}}.py --dataset {{DATASET}} --seed {{DEFAULT_SEED}}` | All methods complete; `over_budget=false`; required fields logged |
| {{N}}.2 | Multi-seed stability | Repeat for each seed in `{{SEED_LIST}}` | All seeds complete; dispersion computable |
| {{N}}.3 | Verify budget match | Assert equal `budget_used` across methods per seed | Budget parity confirmed |
| {{N}}.4 | Verify init weights *(if applicable)* | Forward-pass equality check at run start | Identical starting point confirmed |
| {{N}}.5 | Verify output schema | Validate `summary.json` against schema | All required fields present |

**Gate Definition of Done:**
- [ ] All method × seed combinations complete
- [ ] `over_budget` is `false` for all runs (or flagged + excluded)
- [ ] Budget equality verified across methods within this part
- [ ] Init weight consistency verified *(where required)*
- [ ] `summary.json` schema validation passes
- [ ] `config_resolved.yaml` written for every run
- [ ] **All tradeoff decisions from this phase logged in DECISION_LOG.md**

**Integration hooks:**
- RISK_REGISTER: Verify all Phase {{N}} risks are addressed (see phase-gate risk ownership table)
- DECISION_LOG: **Mandatory** — Record all ADRs (e.g., threshold values, method-specific choices, attack selection rationale, defense strategy decisions). Every phase should produce at least 1 ADR.
- CHANGELOG: Record any `CONTRACT_CHANGE` commits triggered during experiments
- TASK_BOARD: Mark all Phase {{N}} tasks Done

---

### Phase {{N+1}} — Final Evaluation & Artifact Assembly

**Goal:** Test split accessed once; all figures/tables generated; manifests verified.

| # | Step | Command | DoD |
|---|------|---------|-----|
| {{N+1}}.1 | Final eval | `python scripts/final_eval.py --seed {{DEFAULT_SEED}}` | Test split accessed once; `final_eval_results.json` written |
| {{N+1}}.2 | Generate artifacts | `python scripts/{{PRODUCER_SCRIPT}} --seed {{DEFAULT_SEED}}` | All figures/tables produced; no re-training |
| {{N+1}}.3 | Verify manifests | `python scripts/verify_manifests.py` | Exits 0; SHA-256 verified; zero mismatches, zero missing |
| {{N+1}}.4 | Verify no test leakage | Grep per-run outputs for test metric keys | Zero matches outside `final_eval_results.json` |
| {{N+1}}.5 | Determinism check | Re-run producer script; compare hashes | Identical outputs on re-run |

**Gate Definition of Done:**
- [ ] `final_eval_results.json` contains test metrics for all datasets
- [ ] All required figures present in `outputs/figures/`
- [ ] All required tables present in `outputs/tables/`
- [ ] `verify_manifests.py` exits 0
- [ ] No test metric keys in per-run outputs
- [ ] Summary table has all required columns + baseline row
- [ ] Test metrics in tables match `final_eval_results.json` exactly

**Integration hooks:**
- RISK_REGISTER: Re-scan ALL High-severity risks (final delivery gate)
- TASK_BOARD: Mark Phase {{N+1}} tasks Done

---

### Phase {{N+2}} — Report Writing & Delivery

**Goal:** Report + REPRO delivered by delivery date.

| Step | Action | DoD |
|------|--------|-----|
| Draft report | Write in LaTeX editor; ≤ page limit | Paragraph prose; figures with takeaways; hypotheses resolved |
| AI Use Statement | Add per requirements | Present before References |
| REPRO document | Write with all reproduction details | Report link, Git SHA, commands, seeds, EDA confirmation |
| Push code | Push to designated repository | SHA matches REPRO |
| Pre-flight checklist | Run full checklist | All items pass |
| Deliver | Upload to delivery platform | By delivery date |

---

## 3) Iteration Loop

### 3.1 Pick a Task

1. Read TASK_BOARD to find the next unblocked task in the current phase
2. Verify all dependencies are Done
3. Prefer tasks in ID order within a phase

### 3.2 Implement

1. Read the canonical spec docs for the task
2. Read existing code before modifying (never write blind)
3. Implement the minimum change to satisfy the DoD
4. Do NOT invent numeric budgets — read from config
5. Do NOT access test split except in final_eval
6. Do NOT add features beyond the task scope

### 3.3 Test

1. Run the command in the task's DoD
2. Verify exit code is 0
3. Verify output files exist with expected schema
4. Run relevant checks (leakage, budget match, etc.)

### 3.4 Record Provenance

1. Verify provenance files were written
2. If CONTRACT_CHANGE needed, follow §5 below
3. Commit with descriptive message

### 3.5 Update Logs

1. Update TASK_BOARD: mark task Done
2. If a decision was made: add ADR to DECISION_LOG
3. If a contract changed: add entry to CHANGELOG
4. Move to next task

### 3.6 Phase Gate Check

1. When all tasks in a phase are Done, run gate checks
2. If all pass, proceed
3. If any fail, fix and re-run

---

## 4) Change Control

### 4.1 When CONTRACT_CHANGE Is Required

| Category | Examples | Contract Reference |
|----------|---------|-------------------|
| Environment | Python version, dependencies | ENVIRONMENT_CONTRACT §11 |
| Data | Paths, splits, preprocessing | DATA_CONTRACT §9 |
| Experiments | Budgets, method lists, init protocol, output schemas | EXPERIMENT_CONTRACT change control section |
| Metrics | Definitions, thresholds, sanity checks | METRICS_CONTRACT §10 |
| Scripts | Filenames, CLI flags, outputs | SCRIPT_ENTRYPOINTS_SPEC §8 |
| Figures/Tables | Definitions, columns, captions | FIGURES_TABLES_CONTRACT §8 |
| Artifacts | Run ID, manifests, hashing | ARTIFACT_MANIFEST_SPEC §9 |

### 4.2 How to Record

1. **DECISION_LOG** — Add ADR entry (if architectural decision)
2. **Make the change** — Edit contract/config/code
3. **CHANGELOG** — Add change item entry
4. **Commit** — `git commit -m "CONTRACT_CHANGE: [description]"`
5. **Regenerate** — Re-run impacted downstream artifacts

---

## 5) Stop-Ship Checks

Run ALL before delivery. **CRITICAL** items risk invalidation or critical compliance failure. Each check includes a verification command or procedure.

### Data Integrity (CRITICAL)

| # | Check | Verification Command |
|---|-------|---------------------|
| 1 | Correct datasets used | `python scripts/check_data_ready.py` exits 0 |
| 2 | No preprocessing leakage | `python scripts/check_leakage.py` exits 0 |
| 3 | Test split accessed once via final_eval only | `grep -r "test_accuracy\|test_f1" outputs/` — matches only in `final_eval_results.json` |

### Compute Discipline (CRITICAL)

| # | Check | Verification Command |
|---|-------|---------------------|
| 4 | Budgets matched within each part | Parse `summary.json` per part; assert equal `budget_used` |
| 5 | Same init weights where required | Forward-pass equality check from saved `state_dict` |
| 6 | Cross-part budget constraints | Assert linked budget keys are equal per `{{BUDGET_CONFIG}}` |
| 7 | Over-budget runs marked + excluded | Check `over_budget` field; verify excluded from head-to-head claims |
| 8 | Reproducible on target platform | Re-run representative experiment; verify identical outputs |

### Metrics (CRITICAL)

| # | Check | Verification Command |
|---|-------|---------------------|
| 9 | Required metrics per dataset | Verify keys in `final_eval_results.json` |
| 10 | Sanity checks run and reported | `ls outputs/sanity_checks/` — expected files present |
| 11 | Dispersion shown (median + IQR) | Review all seed-aggregated claims for dispersion |

### Artifacts (CRITICAL)

| # | Check | Verification Command |
|---|-------|---------------------|
| 12 | All required figures present | `ls outputs/figures/` — all expected files |
| 13 | All required tables present | `ls outputs/tables/` — all expected files |
| 14 | Summary table has required columns + baseline | Inspect T1 CSV for locked columns |
| 15 | Manifests verified | `python scripts/verify_manifests.py` exits 0 |

### Report Compliance

| # | Check | Severity | Verification |
|---|-------|----------|-------------|
| 16 | Within page limit | CRITICAL | Page count check |
| 17 | Paragraph prose in analysis (no excess bullets) | CRITICAL | Manual review |
| 18 | Hypotheses stated before experiments | CRITICAL | Present in report before results |
| 19 | Hypotheses resolved with quantitative evidence | CRITICAL | Present in conclusion with numbers |
| 20 | Baseline comparison per dataset | CRITICAL | In text + summary table |
| 21 | Decision rule in conclusion | CRITICAL | Practical recommendation present |
| 22 | Failures explained, causes attributed | CRITICAL | Divergence/plateaus discussed |
| 23 | Figure/table captions have takeaways | CRITICAL | Every caption includes interpretation |
| 24 | AI Use Statement present | IMPORTANT | Search for "AI Use Statement" |
| 25 | Sufficient peer-reviewed references | IMPORTANT | Count bibliography entries |
| 26 | READ-ONLY link present | IMPORTANT | Verify link opens in incognito |
| 27 | Two deliverables released | CRITICAL | Report + REPRO submitted |

---

## 6) Canonical Spec Pointers

| Topic | Document | Key Sections |
|-------|----------|-------------|
| Environment, commands, CPU rule | ENVIRONMENT_CONTRACT | Setup, commands, determinism, change control |
| Data paths, splits, leakage | DATA_CONTRACT | Splits, leakage, preprocessing, acceptance |
| Experiment protocol, budgets | EXPERIMENT_CONTRACT | Budgets, init, per-part protocols, exit gates |
| Metric definitions, thresholds | METRICS_CONTRACT | Metrics, threshold, sanity checks, logging |
| Figures, tables, captions | FIGURES_TABLES_CONTRACT | Figure/table defs, captions, acceptance |
| Script CLIs, flags, outputs | SCRIPT_ENTRYPOINTS_SPEC | Conventions, per-script specs, repro sequence |
| Manifests, hashing | ARTIFACT_MANIFEST_SPEC | Run ID, provenance, manifests, hashing |
| Risk tracking | RISK_REGISTER | Full document |
| Task dependencies | TASK_BOARD | Phase tables, critical path |
| Report structure | REPORT_ASSEMBLY_PLAN | Outline, figures, baselines, hypotheses, checklist |
| Decisions | DECISION_LOG | ADR entries |
| Change history | CHANGELOG | Chronological entries |
