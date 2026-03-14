# ARTIFACT MANIFEST SPECIFICATION

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
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §5 for per-run output structure and required files

**Downstream (depends on this contract):**
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §5 for manifest verification scripts (`verify_manifests.py`)
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §7 for artifact acceptance criteria

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{RUN_ID_FORMAT}}` | Run ID naming scheme | `{part}_{dataset}_{method}_seed{seed}` |
| `{{HASH_ALGORITHM}}` | Hashing algorithm | SHA-256 |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This specification defines how experiment outputs are identified, hashed, and recorded for the **Adversarial ML on Network Intrusion Detection** project. It ensures that every artifact can be verified for integrity and traced to its producing run.

---

## 2) Run Identity & Naming

### 2.1 Run ID Format

Every experiment run MUST be assigned a deterministic `run_id` constructed as:

```
{{RUN_ID_FORMAT}}
```

**Components:**
- `part`: experiment part identifier (e.g., `part1`, `part2`, `final_eval`, `sanity_check`)
- `dataset`: dataset name (lowercase)
- `method`: algorithm or technique name (lowercase, underscores)
- `seed`: integer seed value

**Examples:**
- `part1_adult_rhc_seed42`
- `part2_adult_adam_seed123`
- `final_eval_adult_seed42`
- `sanity_check_adult_dummy_seed42`

### 2.2 Run ID Rules

- `run_id` MUST be **deterministic**: identical inputs (part, dataset, method, seed) MUST produce the identical `run_id`
- DO NOT include timestamps, UUIDs, or hostnames in the `run_id`
- `run_id` MUST appear in `summary.json` (key: `"run_id"`) and `run_manifest.json` (key: `"run_id"`)
- `run_id` MUST match the directory path: `outputs/{part}/{dataset}/{method}/seed_{seed}/`

**Verification:** For each run directory, assert `summary.json["run_id"] == run_manifest.json["run_id"]` and both match the directory path components.

### 2.3 Output Directory

Each run's outputs go to:

```
outputs/{{PART}}/{{DATASET}}/{{METHOD}}/seed_{{SEED}}/
```

---

## 3) Required Provenance Files Per Run

Every run directory MUST contain:

| File | Format | Contents |
|------|--------|----------|
| `metrics.csv` | CSV | Per-step metrics |
| `summary.json` | JSON | Run summary |
| `config_resolved.yaml` | YAML | Full resolved configuration |
| `run_manifest.json` | JSON | {{HASH_ALGORITHM}} hashes of all files in this run |

### 3.1 `config_resolved.yaml` Requirements

The `config_resolved.yaml` file is the single source of truth for what a run actually used. It MUST include:

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | str | Deterministic run ID (§2.1) |
| `timestamp_utc` | str | ISO 8601 timestamp |
| `git_sha` | str | Git commit SHA at run time |
| `seed` | int | Random seed |
| `dataset` | str | Dataset name |
| `method` | str | Algorithm/technique name |
| `budget_type` | str | `grad_evals`, `func_evals`, or `episodes` |
| `budget_value` | int | Allocated budget |
| `scoring_metric` | str | Primary metric name |
| `scoring_direction` | str | `minimize` or `maximize` |
| All hyperparameters | varies | Every tunable parameter that affects run behavior |
| `_resolution_sources` | dict | *(Recommended)* Which config level provided each key |

**Rule:** `config_resolved.yaml` MUST be written **before** the run begins (not reconstructed after). It MUST be included in the per-run manifest hash.

**Verification:** `config_resolved.yaml` timestamp precedes `metrics.csv` first entry timestamp. `run_manifest.json` includes a hash entry for `config_resolved.yaml`.

See [CONFIGURATION_SPEC](CONFIGURATION_SPEC.tmpl.md) §4 for full resolved config dump requirements.

### 3.2 Run Manifest Schema (`run_manifest.json`)

```json
{
  "run_id": "{{RUN_ID}}",
  "timestamp_utc": "2026-01-01T00:00:00Z",
  "files": {
    "metrics.csv": {
      "sha256": "abc123...",
      "size_bytes": 12345
    },
    "summary.json": {
      "sha256": "def456...",
      "size_bytes": 678
    },
    "config_resolved.yaml": {
      "sha256": "ghi789...",
      "size_bytes": 432
    }
  }
}
```

---

## 4) Global Provenance Files

In addition to per-run provenance, the project MUST maintain global provenance files written once per full reproduction sequence.

### 4.1 Provenance Triplet

Three files in `outputs/provenance/` form the global provenance record:

| File | Contents | When Written |
|------|----------|-------------|
| `versions.txt` | Python version + all key library versions + platform info | Start of reproduction sequence |
| `git_commit_sha.txt` | Output of `git rev-parse HEAD`; second line "dirty" if working tree is dirty | Start of reproduction sequence |
| `run_log.json` | Ordered list of run_ids executed with exit codes and wall-clock times | Updated after each run |

#### `versions.txt` Schema

```
python: 3.11
numpy: <version>
pandas: <version>
scikit-learn: <version>
matplotlib: <version>
torch: <version>
platform: <platform string>
machine: <architecture>
cuda_available: <bool>
```

#### `run_log.json` Schema

```json
{
  "timestamp_utc": "<ISO 8601>",
  "runs": [
    {"run_id": "<str>", "script": "<str>", "exit_code": 0, "wall_clock_sec": 0.0}
  ]
}
```

**Note:** Timestamps in `run_log.json` are for audit only. They MUST NOT appear in any artifact used for reproducibility hashing.

### 4.2 Provenance in Global Manifest

The global manifest (§5) MUST reference the provenance files:

```json
{
  "provenance": {
    "versions_txt_sha256": "<hex string>",
    "git_commit_sha_txt_sha256": "<hex string>"
  }
}
```

---

## 5) Global Artifact Manifest

A single global manifest records all runs and report-ready artifacts.

**Path:** `outputs/artifact_manifest.json`

**Producer:** `{{PRODUCER_SCRIPT}}` (generated as the final step of artifact assembly)

### 4.1 Schema

```json
{
  "project": "Adversarial ML on Network Intrusion Detection",
  "generated_utc": "2026-01-01T00:00:00Z",
  "git_sha": "abc123...",
  "runs": {
    "{{RUN_ID_1}}": {
      "manifest_path": "outputs/part1/.../run_manifest.json",
      "manifest_sha256": "..."
    }
  },
  "figures": {
    "f1_loss_vs_wallclock.pdf": {
      "sha256": "...",
      "size_bytes": 12345
    }
  },
  "tables": {
    "t1_summary_table.csv": {
      "sha256": "...",
      "size_bytes": 678
    }
  }
}
```

---

## 5) Hashing & Integrity Rules

### 5.1 Algorithm

All hashes use **{{HASH_ALGORITHM}}** (e.g., SHA-256).

### 5.2 What Gets Hashed

- Every file in every run directory
- Every generated figure and table
- The global manifest itself (recorded in verification output)

### 5.3 Determinism Requirement

Running the same experiment with the same seed, data, and environment MUST produce **byte-identical outputs** (excluding timestamps in `run_log.json`). This is non-negotiable.

**What MUST be deterministic:**
- `metrics.csv` — identical values at every step
- `summary.json` — identical final metrics and budget accounting
- `config_resolved.yaml` — identical resolved configuration
- Figure PDFs — identical renderings (no random jitter, timestamps, or non-deterministic layout)
- Table CSVs — identical rows and values

**What MAY vary:**
- `run_log.json` timestamps (audit only, not used for hashing)
- Log file timestamps (if logs are not hashed)

**Verification:** Run the same experiment twice with the same seed. Compare SHA-256 hashes of all output files. If any hash differs, investigate and fix before locking the manifest.

**Forbidden in hashed artifacts:** timestamps, random UUIDs, host-specific paths, non-deterministic float formatting. Use fixed-precision formatting for all numeric values in CSVs.

### 5.4 Verification

```bash
python scripts/verify_manifests.py
```

This script MUST:
1. Load `artifact_manifest.json`
2. Recompute {{HASH_ALGORITHM}} for every listed file
3. Compare against recorded hashes
4. Exit 0 if all match, exit 1 on any mismatch or missing file
5. Print a summary: `N files verified, 0 mismatches, 0 missing`

---

## 6) Results Artifact Schemas

*(Define schemas for any aggregated result files beyond per-run outputs.)*

### Heatmap CSVs (if applicable)

```csv
alpha,beta1,val_loss,reached_l,steps_to_l
0.001,0.9,0.342,true,5000
...
```

### Stability Summary (if applicable)

```json
{
  "method": "adam",
  "seeds": [42, 123, 456, 789, 1024],
  "best_val_loss": {"median": 0.33, "iqr": [0.32, 0.34]},
  "test_f1": {"median": 0.75, "iqr": [0.73, 0.77]}
}
```

*(Add schemas for your project-specific aggregated results.)*

---

## 7) Interaction with Figures & Tables

The artifact generation script (`{{PRODUCER_SCRIPT}}`) MUST:

1. Discover all run manifests under `outputs/`
2. Load `final_eval_results.json` for test metrics
3. Generate all figures and tables
4. Record everything in the global manifest
5. NOT re-run any training or evaluation

---

## 8) Phase Gates / Acceptance Checklist

- [ ] Every run directory has a `run_manifest.json`
- [ ] Global `artifact_manifest.json` exists and is complete
- [ ] `verify_manifests.py` exits 0 (all hashes match)
- [ ] No orphan files (files in output dirs not recorded in manifests)
- [ ] Determinism check: re-running producer script produces identical hashes

---

## 9) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Run ID naming scheme
- Provenance file requirements or formats
- Manifest schemas (run or global)
- Results artifact schemas
- Hashing algorithm or rules
- Discovery or data-flow rules in the producer script
