# SCRIPT ENTRYPOINTS SPECIFICATION

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §8 for data acceptance tests (Phase 0 checks)
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §5 for environment setup commands
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §6-N for per-part experiment protocols
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §7 for sanity check requirements
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §2 for artifact generation rules
- See [ARTIFACT_MANIFEST_SPEC](ARTIFACT_MANIFEST_SPEC.tmpl.md) §5 for hashing and integrity verification

**Downstream (depends on this contract):**
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for phase commands referencing these scripts

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{BUDGET_CONFIG}}` | Budget config file path | config/budgets.yaml |
| `{{SPLITS_DIR}}` | Split files directory | data/splits/ |
| `{{OUTPUT_DIR}}` | Default output directory | outputs/ |
| `{{DEFAULT_SEED}}` | Default random seed | 42 |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This specification defines every script entrypoint for the **Adversarial ML on Network Intrusion Detection** project: its filename, CLI flags, inputs, outputs, and exit codes.

**Stability policy:** Script filenames and CLI flag names are part of the contract. Renaming a script or changing a flag name/type/default is a `CONTRACT_CHANGE`.

---

## 2) Global CLI Conventions

All experiment scripts share these conventions:

### 2.1 Shared Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--seed` | int | {{DEFAULT_SEED}} | Random seed |
| `--output_dir` | str | `{{OUTPUT_DIR}}` | Root output directory |
| `--budgets_path` | str | `{{BUDGET_CONFIG}}` | Budget configuration file |
| `--splits_dir` | str | `{{SPLITS_DIR}}` | Split files directory |

### 2.2 Budget Override Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--budget_func_evals` | int | from config | Override function evaluation budget |
| `--budget_grad_evals` | int | from config | Override gradient evaluation budget |

### 2.3 Config Resolution Hierarchy

When a parameter can be set in multiple places, the resolution order is:

1. **CLI flag** (highest priority)
2. **Budget config file** (`{{BUDGET_CONFIG}}`)
3. **Hard-coded default** (lowest priority)

The fully resolved configuration MUST be saved as `config_resolved.yaml` in every run directory.

### 2.4 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Fatal error (bad input, missing dependency, assertion failure) |
| 2 | Budget exceeded (run completed but over budget) |

---

## 3) Phase 0 Scripts (Verification & Setup)

### 3.1 `scripts/verify_env.sh`

| Property | Value |
|----------|-------|
| **Purpose** | Verify environment matches contract |
| **Inputs** | Active conda/mamba environment |
| **Outputs** | stdout: version strings |
| **Exit code** | 0 if all versions match; 1 otherwise |

### 3.2 `scripts/check_data_ready.py`

| Property | Value |
|----------|-------|
| **Purpose** | Verify raw data files present at canonical paths |
| **Inputs** | `data/raw/` directory |
| **Outputs** | stdout: file presence checklist |
| **Exit code** | 0 if all files present; 1 otherwise |

### 3.3 `scripts/check_leakage.py`

| Property | Value |
|----------|-------|
| **Purpose** | Run leakage tripwires (LT-1 through LT-N) |
| **Inputs** | Splits, preprocessing code |
| **Outputs** | stdout: tripwire pass/fail summary |
| **Exit code** | 0 if all pass; 1 if any fail |

*(Add project-specific Phase 0 scripts as needed: split conversion, snapshot verification, etc.)*

---

## 4) Phase 1 Scripts (Experiments)

### 4.1 `scripts/run_eda.py`

| Property | Value |
|----------|-------|
| **Purpose** | Run exploratory data analysis |
| **Flags** | `--dataset {name}`, `--seed` |
| **Outputs** | `outputs/eda/{{DATASET}}_eda_summary.json` |

### 4.2 `scripts/run_sanity_checks.py`

| Property | Value |
|----------|-------|
| **Purpose** | Run dummy baseline and shuffled-label baseline |
| **Flags** | `--dataset {name}`, `--seed` |
| **Outputs** | `outputs/sanity_checks/dummy_baseline_{{DATASET}}.json`, `shuffled_label_baseline_{{DATASET}}.json` |

### 4.3-N Experiment Scripts

*(Define one subsection per experiment script. Template:)*

### `scripts/run_{{PART_NAME}}.py`

| Property | Value |
|----------|-------|
| **Purpose** | *(What this script does)* |
| **Flags** | `--dataset`, `--seed`, `--algo` *(if applicable)*, budget overrides |
| **Inputs** | Splits, init weights, budget config |
| **Outputs** | `outputs/{{PART}}/{{DATASET}}/{{METHOD}}/seed_{{SEED}}/` containing metrics.csv, summary.json, config_resolved.yaml, run_manifest.json |
| **Test-split access** | **FORBIDDEN** — raises ValueError if attempted |
| **Budget enforcement** | Hard-stop at budget limit; sets `over_budget` flag |

---

## 5) Phase 2 Scripts (Post-Experiment)

### 5.1 `scripts/final_eval.py`

| Property | Value |
|----------|-------|
| **Purpose** | Run final evaluation on test split (ONCE) |
| **Flags** | `--seed` |
| **Inputs** | All experiment outputs, splits |
| **Outputs** | `outputs/final_eval/seed_{{SEED}}/final_eval_results.json` |
| **Test-split access** | **AUTHORIZED** — this is the ONLY script allowed to access test indices |
| **Constraint** | Must load trained models, not retrain |

### 5.2 `scripts/make_report_artifacts.py`

| Property | Value |
|----------|-------|
| **Purpose** | Generate all report figures and tables |
| **Flags** | `--seed` |
| **Inputs** | All experiment outputs, `final_eval_results.json`, baseline config |
| **Outputs** | `outputs/figures/`, `outputs/tables/`, `outputs/artifact_manifest.json` |
| **Constraint** | Deterministic; no re-training; reads only from existing outputs |

### 5.3 `scripts/verify_manifests.py`

| Property | Value |
|----------|-------|
| **Purpose** | Verify integrity of all artifact hashes |
| **Inputs** | `outputs/artifact_manifest.json` |
| **Outputs** | stdout: verification summary |
| **Exit code** | 0 if all hashes match; 1 on any mismatch |

---

## 6) Minimal Reproduction Sequence

The canonical execution order for full reproduction:

```bash
# Phase 0: Setup
bash scripts/verify_env.sh
python scripts/check_data_ready.py
python scripts/check_leakage.py

# Phase 1: EDA + Sanity Checks
python scripts/run_eda.py --dataset {{DATASET_1}} --seed {{DEFAULT_SEED}}
python scripts/run_eda.py --dataset {{DATASET_2}} --seed {{DEFAULT_SEED}}
python scripts/run_sanity_checks.py --dataset {{DATASET_1}} --seed {{DEFAULT_SEED}}

# Phase 1: Experiments (repeat per seed in stability list)
# (Fill in experiment commands per part)

# Phase 2: Final evaluation and artifacts
python scripts/final_eval.py --seed {{DEFAULT_SEED}}
python scripts/make_report_artifacts.py --seed {{DEFAULT_SEED}}
python scripts/verify_manifests.py
```

---

## 7) Test Suite

```bash
python -m pytest tests/ -v
```

Tests MUST cover:
- Data loading and split integrity
- Preprocessing leakage prevention
- Budget enforcement
- Output schema validation
- Metric computation correctness
- Determinism (same seed → same output)

---

## 8) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Script filenames or paths
- CLI flag names, types, or defaults
- Required outputs (file names, schemas, directory paths)
- Hard constraint additions or removals (budget caps, leakage guards)
- Exit code semantics
- Reproduction sequence ordering
