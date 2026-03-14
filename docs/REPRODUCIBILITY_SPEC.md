# REPRODUCIBILITY SPECIFICATION

<!-- version: 1.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_SL_Report -->

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
- See [ENVIRONMENT_CONTRACT](../core/ENVIRONMENT_CONTRACT.tmpl.md) §5 for environment setup commands and §7 for reproduction commands
- See [DATA_CONTRACT](../core/DATA_CONTRACT.tmpl.md) §2 for canonical data paths and §7 for provenance artifacts
- See [SCRIPT_ENTRYPOINTS_SPEC](../core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §6 for minimal reproduction sequence
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §5 for hashing and integrity verification

**Downstream (depends on this contract):**
- See [PRE_SUBMISSION_CHECKLIST](PRE_SUBMISSION_CHECKLIST.tmpl.md) §4 for reproducibility verification checks

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{REPORT_LINK}}` | Read-only link to report | Overleaf read-only URL, Google Docs viewer link |
| `{{REPO_URL}}` | Repository URL | GitHub repo URL |
| `{{FINAL_COMMIT_SHA}}` | Git SHA of the final delivery commit | abc1234def5678 |
| `{{PLATFORM_OS}}` | Operating system | Ubuntu 20.04 / macOS 14.0 / Windows 11 |
| `{{PLATFORM_CPU}}` | CPU specification | 8 vCPU AMD EPYC / Apple M2 / Intel i7-12700 |
| `{{PLATFORM_RAM}}` | RAM | 32 GiB |
| `{{PLATFORM_GPU}}` | GPU requirement | Not required (CPU-only) / NVIDIA RTX 3090 |
| `conda` | Environment manager | mamba / conda / pip+venv |
| `environment.yml` | Environment definition file | environment.yml / requirements.txt |
| `adversarial-ids` | Environment name | my-ml-project |
| `3.11` | Python version | 3.10.13 |
| `{{DEFAULT_SEED}}` | Default random seed | 42 |
| `{{SEED_LIST}}` | All seeds used | [42, 123, 456, 789, 1024] |
| `{{DATA_SOURCE}}` | Where to obtain data | Kaggle, UCI ML Repository, Canvas |
| `{{DATASET_N_FILE}}` | Dataset filename | adult.csv |
| `{{DATASET_N_DESCRIPTION}}` | Dataset brief | Adult Income (45,222 rows x 15 columns) |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose

This document enables anyone to reproduce **all** artifacts for the **Adversarial ML on Network Intrusion Detection** project from a fresh clone. It is the single document a reviewer needs to go from zero to verified outputs.

**Completeness requirement:** Every command needed to reproduce the project MUST appear in this document. If a command is missing, the project is not reproducible.

---

## 2) Report Link & Repository

| Item | Value |
|------|-------|
| **Report (read-only)** | {{REPORT_LINK}} |
| **Repository** | {{REPO_URL}} |
| **Branch** | `main` |
| **Final commit SHA** | `{{FINAL_COMMIT_SHA}}` |

**Verification:**

```bash
git clone {{REPO_URL}}
cd {{PROJECT_DIR}}
git log --oneline -1
# Expected: {{FINAL_COMMIT_SHA}}
```

---

## 3) Hardware Requirements

| Resource | Specification | Notes |
|----------|--------------|-------|
| **OS** | {{PLATFORM_OS}} | *(tested platform)* |
| **CPU** | {{PLATFORM_CPU}} | *(minimum for reasonable runtime)* |
| **RAM** | {{PLATFORM_RAM}} | *(minimum to avoid OOM)* |
| **GPU** | {{PLATFORM_GPU}} | *(required or optional)* |
| **Disk** | *(estimated)* | *(space for data + outputs)* |

**CPU reproducibility rule:** All final report artifacts MUST be reproducible on CPU. GPU may be used for exploration but MUST NOT be required for delivery artifacts.

---

## 4) Environment Setup

```bash
# 1. Create environment
conda env create -f environment.yml
conda activate adversarial-ids

# 2. Verify environment
bash scripts/verify_env.sh
# Expected: exits 0, prints matching versions
```

### Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python | 3.11 | Runtime |
| *(package)* | *(version)* | *(purpose)* |
| *(add rows from environment.yml)* | | |

---

## 5) Data Acquisition

### Data Sources

| Dataset | Source | Filename | Destination |
|---------|--------|----------|-------------|
| {{DATASET_1_NAME}} | {{DATA_SOURCE}} | `{{DATASET_1_FILE}}` | `data/raw/{{DATASET_1_FILE}}` |
| {{DATASET_2_NAME}} | {{DATA_SOURCE}} | `{{DATASET_2_FILE}}` | `data/raw/{{DATASET_2_FILE}}` |
| *(add rows)* | | | |

### Placement Instructions

```bash
# Download datasets from {{DATA_SOURCE}} and place at:
data/raw/{{DATASET_1_FILE}}    # {{DATASET_1_DESCRIPTION}}
data/raw/{{DATASET_2_FILE}}    # {{DATASET_2_DESCRIPTION}}
```

### Verification

```bash
python scripts/check_data_ready.py
# Expected: exits 0, all files present, SHA-256 hashes match
```

---

## 6) Random Seeds

| Seed | Purpose |
|------|---------|
| `{{DEFAULT_SEED}}` | Default seed for all stochastic operations |
| `{{SEED_LIST}}` | Stability seeds for multi-seed experiments |

All scripts accept `--seed` flag. The default seed controls: data splits, cross-validation fold assignment, model initialization, and NumPy/PyTorch random state.

---

## 7) Reproduction Sequence

All commands run from repository root. Execute in order.

### Phase 0: Environment & Data Verification

```bash
# Verify environment
bash scripts/verify_env.sh

# Verify data
python scripts/check_data_ready.py

# Run leakage tripwires
python scripts/check_leakage.py
```

### Phase 1: EDA

```bash
# Generate EDA artifacts (per dataset)
python scripts/run_eda.py --dataset {{DATASET_1_NAME}} --seed {{DEFAULT_SEED}}
python scripts/run_eda.py --dataset {{DATASET_2_NAME}} --seed {{DEFAULT_SEED}}
```

### Phase 2-N: Experiments

*(Fill in per-part experiment commands. Include all flags, seeds, and budget references.)*

```bash
# Part {{N}}: {{PART_NAME}}
# python scripts/run_{{PART}}.py --dataset {{DATASET}} --seed {{DEFAULT_SEED}} ...
```

*(For multi-seed stability runs, repeat with each seed in {{SEED_LIST}}.)*

### Final: Evaluation & Artifacts

```bash
# Final evaluation (test split accessed ONCE)
python scripts/final_eval.py --seed {{DEFAULT_SEED}}

# Generate all report figures and tables
python scripts/make_report_artifacts.py --seed {{DEFAULT_SEED}}

# Verify artifact integrity
python scripts/verify_manifests.py
# Expected: exits 0, all hashes match
```

---

## 8) EDA Summaries

*(Include per-dataset EDA summaries so reviewers can verify their reproduction matches. This section is filled in after EDA is complete.)*

### {{DATASET_1_NAME}}

```
Shape: *(rows x columns)*
Target: *(target variable and type)*
Features: *(feature count and types)*
Missing values: *(count)*
```

**Class Distribution:**

| Class | Count | Fraction |
|-------|------:|---------:|
| *(class)* | *(count)* | *(fraction)* |

### {{DATASET_2_NAME}}

```
Shape: *(rows x columns)*
Target: *(target variable and type)*
Features: *(feature count and types)*
Missing values: *(count)*
```

**Class Distribution:**

| Class | Count | Fraction |
|-------|------:|---------:|
| *(class)* | *(count)* | *(fraction)* |

---

## 9) Expected Outputs

After running the full reproduction sequence, the following directory structure is produced:

```
outputs/
├── eda/                           # EDA artifacts
│   ├── {{DATASET_1_NAME}}_eda_summary.json
│   └── {{DATASET_2_NAME}}_eda_summary.json
├── sanity_checks/                 # Sanity check results
├── {{PART_N}}/                    # Per-part experiment outputs
│   └── {{DATASET}}/{{METHOD}}/seed_{{SEED}}/
│       ├── metrics.csv
│       ├── summary.json
│       ├── config_resolved.yaml
│       └── run_manifest.json
├── final_eval/                    # Final test evaluation
├── figures/                       # Report figures
├── tables/                        # Report tables
└── artifact_manifest.json         # Global integrity manifest
```

### Verification

```bash
# Verify all manifests
python scripts/verify_manifests.py
# Expected: "N files verified, 0 mismatches, 0 missing"

# Run test suite
python -m pytest tests/ -v
# Expected: all tests pass
```

---

## 10) Determinism Guarantee

Running the full reproduction sequence with the same seed, data, and environment MUST produce byte-identical outputs (excluding timestamps in logs). If outputs differ, the determinism contract (ENVIRONMENT_CONTRACT §8) has been violated.

**Quick verification:** Compare `artifact_manifest.json` hashes between two independent runs with the same seed.

---

## 11) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit and an update to this document:

- Environment file or Python version
- Data acquisition procedure or file paths
- Reproduction sequence (commands, ordering, flags)
- Random seeds
- Expected output structure
- Hardware requirements
