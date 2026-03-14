# RISK REGISTER

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
- See [DATA_CONTRACT](../core/DATA_CONTRACT.tmpl.md) §4 for leakage prevention rules (Category A risks)
- See [EXPERIMENT_CONTRACT](../core/EXPERIMENT_CONTRACT.tmpl.md) §2 for budget-matching rules (Category C risks)
- See [METRICS_CONTRACT](../core/METRICS_CONTRACT.tmpl.md) §5 for threshold governance (Category B risks)
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §5 for integrity rules (Category E risks)
- See [SCRIPT_ENTRYPOINTS_SPEC](../core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §2 for exit codes used by automation hooks

**Downstream (depends on this contract):**
- See [IMPLEMENTATION_PLAYBOOK](IMPLEMENTATION_PLAYBOOK.tmpl.md) §5 for stop-ship checks sourced from this register
- See [CHANGELOG](CHANGELOG.tmpl.md) for risk mitigation cross-references per change entry

## Adversarial ML on Network Intrusion Detection — Risk Register

**Status:** Living document; review at every phase gate.

---

### Purpose

This register catalogues risks that can invalidate runs, fail acceptance criteria, or block delivery. Every entry is anchored to a specific requirement. The register is action-oriented: each risk has a concrete detection test, a mitigation step, and a phase-gate owner.

### How to Use

- **When to review:** At every phase gate and before delivery. Re-scan all High-severity rows before final release.
- **How to update:** Add new risks via `CONTRACT_CHANGE` commit. Mark mitigated risks as `CLOSED` with the commit SHA. Do not delete rows.
- **Owner codes:** `Data` = data pipeline | `Training` = experiment scripts | `Eval` = evaluation/metrics | `Report` = report writing

---

### Top Critical Invalidators

Issues that, if present at delivery, result in **critical invalidation or non-compliance**. These are non-negotiable — a single failure here can invalidate all downstream results.

| # | Invalidator | Consequence | Detection |
|---|------------|-------------|-----------|
| 1 | **Wrong datasets** | All results invalid | `check_data_ready.py` verifies file hashes |
| 2 | **Preprocessing leakage** (fit on full data) | All metrics inflated | `check_leakage.py` LT-1, LT-3 |
| 3 | **Test used for tuning** | Selection bias; results unreliable | `check_leakage.py` LT-2; grep for test metrics in per-run outputs |
| 4 | **Unequal budgets in comparisons** | Unfair comparison; claims invalid | Assert equal `budget_used` across methods per part |
| 5 | **Missing required metrics** | Incomplete evaluation | Schema validation of `summary.json` |
| 6 | *(Add project-specific invalidators)* | | |

**Rule:** Every critical invalidator MUST have an automated detection test. Manual-only detection is insufficient for critical risks.

**Verification:** For each row in the critical invalidators table, verify the "Detection" column references a script that exits non-zero on failure. Run each detection script and confirm exit 0.

---

### Risk Taxonomy

Risks are organized into 8 categories. Each category maps to a contract domain:

| Category | Domain | Primary Contract |
|----------|--------|-----------------|
| **A** | Data & Leakage | DATA_CONTRACT §3-4 |
| **B** | Evaluation Discipline | METRICS_CONTRACT §5, §7 |
| **C** | Compute Fairness | EXPERIMENT_CONTRACT §2 |
| **D** | Method-Specific Pitfalls | EXPERIMENT_CONTRACT §6-N |
| **E** | Optimizer/Ablation Confounds | EXPERIMENT_CONTRACT §4 |
| **F** | Artifact & Repro | ARTIFACT_MANIFEST_SPEC §3-5 |
| **G** | Report Compliance | REPORT_ASSEMBLY_PLAN, AI_DIVISION_OF_LABOR |
| **H** | Prior Work & Reuse | PRIOR_WORK_REUSE §5-10 |

---

### Risk Table

| ID | Risk | Source | Sev | Lklhd | Detection Test | Mitigation | Owner | Gate |
|----|------|--------|-----|-------|----------------|------------|-------|------|
| **A — Data & Leakage** | | | | | | | | |
| R-A1 | Dataset mismatch | *(cite)* | High | Low | `check_data_ready.py` exits 0; SHA-256 match | Lock paths; verify hashes | Data | Phase 0 |
| R-A2 | Preprocessing leakage (fit on full data) | *(cite)* | High | Med | `check_leakage.py` LT-1, LT-3 | `pipeline.fit(X_train)` only | Data | Phase 0 |
| R-A3 | Test split accessed prematurely | *(cite)* | High | Med | `check_leakage.py` LT-2 | `allow_test=False` default | Data | Phase 0 |
| R-A4 | Split drift from prior project | *(cite)* | High | Low | Hash comparison against provenance | Lock splits; CONTRACT_CHANGE for edits | Data | Phase 1 |
| R-A5 | Label mapping error | *(cite)* | Med | Med | Sanity check: dummy F1 ≈ 0 for minority | Hard-code and test label mapping | Data | Phase 1 |
| **B — Evaluation Discipline** | | | | | | | | |
| R-B1 | Test used more than once | *(cite)* | High | Low | Grep for test metric keys in per-run outputs | Single test-access path (`final_eval.py`) | Eval | Phase 2 |
| R-B2 | Wrong metric definition | *(cite)* | High | Low | Assert correct sklearn call signature in config | Centralize metric computation | Eval | Phase 1 |
| R-B3 | Threshold changed after experiments | *(cite)* | High | Med | Git log for budget config edits | Lock via CONTRACT_CHANGE before experiments | Eval | Phase 1 |
| R-B4 | Missing seed dispersion | *(cite)* | High | Med | Assert seed list populated; multi-seed outputs exist | Run all seeds; report median + IQR | Training | Phase 1 |
| R-B5 | Missing sanity checks | *(cite)* | Med | Med | Check for `outputs/sanity_checks/` files | Run before main experiments | Eval | Phase 1 |
| **C — Compute Fairness** | | | | | | | | |
| R-C1 | Mismatched budgets across methods | *(cite)* | High | Med | Assert equal `budget_used` across methods per seed | Scripts enforce budget cap; hard-stop at limit | Training | Phase 1 |
| R-C2 | Cross-part budget mismatch | *(cite)* | High | Med | Assert linked part budgets are equal | Shared config key; validated at Phase 0 | Training | Phase 0 |
| R-C3 | Over-budget runs in head-to-head claims | *(cite)* | Med | Low | Check `over_budget` flag in summary tables | Mark and exclude over-budget runs | Eval | Phase 2 |
| **D — Method-Specific Pitfalls** | | | | | | | | |
| R-D1 | *(e.g.)* Non-deterministic evaluation during RO | *(cite)* | High | Med | Assert `model.eval()` + `dropout_off` + `bn_frozen` in summary | Wrap evaluation with determinism guards | Training | Phase 1 |
| R-D2 | *(e.g.)* Missing operator disclosures in captions | *(cite)* | High | Med | Check figure captions for required settings | Read from `config_resolved.yaml` in producer script | Report | Phase 2 |
| *(Add project-specific method risks)* | | | | | | | | |
| **E — Optimizer/Ablation Confounds** | | | | | | | | |
| R-E1 | Different initial weights across compared methods | *(cite)* | High | Med | Forward-pass equality check at run start | Load saved `state_dict` per seed; verify | Training | Phase 1 |
| R-E2 | Hidden hyperparameter mismatch (e.g., weight_decay) | *(cite)* | Med | Med | Diff `config_resolved.yaml` across methods | Log every hyperparameter explicitly | Training | Phase 1 |
| R-E3 | HP retuning in dependent parts | *(cite)* | High | Med | Diff HP config between parts | Lock HPs from prior part; load from fixed config | Training | Phase 1 |
| *(Add project-specific confound risks)* | | | | | | | | |
| **F — Artifact & Repro** | | | | | | | | |
| R-F1 | Missing provenance files | *(cite)* | Med | Med | `verify_manifests.py` exits 0 | First run writes provenance triplet | Report | Phase 2 |
| R-F2 | Missing figures/tables | *(cite)* | High | Low | Producer script errors on missing input | Script fails loud, not silent | Eval | Phase 2 |
| R-F3 | Test metrics outside final_eval | *(cite)* | High | Low | Grep per-run outputs for test keys | Centralize in `final_eval.py` | Eval | Phase 2 |
| R-F4 | Non-deterministic figure rebuild | *(cite)* | Med | Low | Run producer twice; compare hashes | No timestamps or random jitter in figures | Eval | Phase 2 |
| **G — Report Compliance** | | | | | | | | |
| R-G1 | Exceeds page limit | *(cite)* | High | Med | Page count check | Tighten prose, reduce figure sizes | Report | Phase 3 |
| R-G2 | Excess bullets (not prose) | *(cite)* | High | Med | Visual scan of Analysis/Discussion | Write analysis as paragraphs | Report | Phase 3 |
| R-G3 | Missing hypotheses or resolution | *(cite)* | High | Med | Search report for hypothesis section | Write before experiments; resolve with evidence | Report | Phase 1 |
| R-G4 | Missing baseline comparison | *(cite)* | Med | Med | Search for baseline reference | Include baseline row in summary table | Report | Phase 3 |
| R-G5 | Missing AI Use Statement | *(cite)* | Med | Low | Ctrl-F report for "AI Use Statement" | Add before References | Report | Phase 3 |
| R-G6 | Figure captions lack takeaway | *(cite)* | Med | Med | Review each caption for interpretation | One takeaway sentence per caption | Report | Phase 3 |
| **H — Prior Work & Reuse** | | | | | | | | |
| R-H1 | Vendor snapshot hash mismatch | *(cite)* | High | Low | `verify_{{PRIOR_PROJECT}}_snapshot.py` exits 0 | Verify at Phase 0 gate | Data | Phase 0 |
| R-H2 | Incompatible code carried over | *(cite)* | Med | Med | Smoke-test extracted code with dummy data | Extract only needed components; exclude incompatible code | Data | Phase 0 |
| R-H3 | Format conversion error | *(cite)* | High | Low | Conversion script integrity checks | Verify no overlap, full coverage, hash match | Data | Phase 0 |

---

### Automation Hooks

Automated checks to fail fast on the highest-severity risks. These can run as pre-commit hooks, CI checks, or manual gate scripts.

| Hook | Risks Covered | Implementation | Trigger | Exit Code |
|------|---------------|----------------|---------|-----------|
| **Data readiness** | R-A1 | `check_data_ready.py` verifies files + hashes | Phase 0 gate | 0 = pass |
| **Leakage tripwire** | R-A2, R-A3 | `check_leakage.py` runs LT-1, LT-2, LT-3 | Pre-experiment | 0 = pass |
| **Vendor snapshot verify** | R-H1, R-H2, R-H3 | `verify_{{PRIOR_PROJECT}}_snapshot.py` | Phase 0 gate | 0 = pass |
| **Test-access guard** | R-A3, R-B1, R-F3 | Grep for test metric keys in per-run outputs | Post-experiment | 0 = no matches |
| **Budget equality** | R-C1, R-C2, R-C3 | Parse `summary.json` per part; assert equal budgets | Post-part | 0 = pass |
| **Init-weight match** | R-E1 | Forward-pass equality check per seed | Start of comparison | 0 = pass |
| **Config schema** | R-B3, R-C2 | Validate required keys in budget config | Phase 0 gate | 0 = pass |
| **Manifest integrity** | R-F1, R-F4 | `verify_manifests.py` recomputes all hashes | Pre-delivery | 0 = pass |

**Integration options:**
- **Pre-commit hook:** Leakage tripwire, test-access guard
- **Phase gate script:** Data readiness, vendor snapshot, config schema, budget equality
- **CI pipeline:** All hooks (if CI is available)

---

### Phase-Gate Risk Ownership

Each phase gate has an owner responsible for verifying all risks assigned to that gate.

| Phase Gate | Owner | Risks to Verify | Gate Script |
|-----------|-------|----------------|-------------|
| **Phase 0** (env + data) | Data | R-A1, R-A2, R-A3, R-C2, R-H1, R-H2, R-H3 | `scripts/gate_phase0.sh` *(or manual checklist)* |
| **Phase 1** (experiments) | Training | R-A4, R-A5, R-B2, R-B3, R-B4, R-B5, R-C1, R-D*, R-E*, R-G3 | Post-part budget + init checks |
| **Phase 2** (artifacts) | Eval | R-B1, R-C3, R-F1, R-F2, R-F3, R-F4 | `verify_manifests.py` + test-access guard |
| **Phase 3** (report) | Report | R-G1, R-G2, R-G4, R-G5, R-G6 | Manual review checklist |
| **Final** (delivery) | Report | All High-severity rows re-scanned | Full checklist |

**Rule:** No phase gate passes unless all assigned High-severity risks have `CLOSED` status or documented mitigation.
