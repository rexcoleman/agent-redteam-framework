# DATA CONTRACT

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
- None — this is a foundational contract.

**Downstream (depends on this contract):**
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for dataset/task metric mapping
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §3 for split usage and leakage prevention in experiments
- See [PRIOR_WORK_REUSE](../management/PRIOR_WORK_REUSE.tmpl.md) §2 for reused data components and split inheritance
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §3 for data verification scripts (`check_data_ready.py`, `check_leakage.py`)
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for Phase 1 data readiness gate

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{DATASET_N_NAME}}` | Human-readable dataset name | IMDB Reviews |
| `{{DATASET_N_FILE}}` | Raw data filename | dataset_a.csv |
| `{{DATASET_N_TASK}}` | ML task type | binary classification |
| `{{DATASET_N_CLASSES}}` | Number of classes or target description | 2 (>50K vs <=50K) |
| `{{DATASET_N_FEATURES}}` | Feature count after preprocessing | 104 after one-hot encoding |
| `{{SPLIT_METHOD}}` | How splits are created/sourced | StratifiedShuffleSplit, prior project, etc. |
| `{{SPLIT_SEED}}` | Seed for split generation | 42 |
| `{{SPLIT_RATIOS}}` | Train/val/test proportions | 64/16/20 |
| `{{PREPROCESSING_STEPS}}` | Per-dataset preprocessing pipeline | StandardScaler, OneHotEncoder, SimpleImputer |
| `{{DATA_SOURCE}}` | Where raw data comes from | Kaggle, UCI ML Repository, Hugging Face |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines the data governance rules for the **Adversarial ML on Network Intrusion Detection** project. It covers:

- Canonical data paths and file formats
- Train/val/test split discipline and storage
- Leakage prevention rules and automated tripwires
- Per-dataset preprocessing protocols
- Data provenance and audit artifacts
- Change control triggers

---

## 2) Canonical Data Paths

| Dataset | Raw Path | Description |
|---------|----------|-------------|
| {{DATASET_1_NAME}} | `data/raw/{{DATASET_1_FILE}}` | {{DATASET_1_TASK}}, {{DATASET_1_CLASSES}} |
| {{DATASET_2_NAME}} | `data/raw/{{DATASET_2_FILE}}` | {{DATASET_2_TASK}}, {{DATASET_2_CLASSES}} |

*(Add rows for additional datasets as needed.)*

Raw data files MUST NOT be committed to git. Add `data/raw/**` to `.gitignore`. Data placement instructions go in the REPRO document.

**Verification:** `git ls-files data/raw/` returns empty. `.gitignore` contains `data/raw/**`.

---

## 3) Split Discipline

### 3.1 Split Source

*(Describe how splits are created: from a prior project, generated fresh, provided by the project specification, etc.)*

**Method:** {{SPLIT_METHOD}}
**Seed:** {{SPLIT_SEED}}
**Ratios:** {{SPLIT_RATIOS}} (train / val / test)

### 3.2 Split Storage Format

Splits are stored as JSON files at `data/splits/{{DATASET_NAME}}/split_seed{{SEED}}.json` with the following schema:

```json
{
  "dataset": "{{DATASET_NAME}}",
  "seed": {{SPLIT_SEED}},
  "source": "{{SPLIT_SOURCE_DESCRIPTION}}",
  "n_total": 0,
  "n_train": 0,
  "n_val": 0,
  "n_test": 0,
  "train_indices": [],
  "val_indices": [],
  "test_indices": [],
  "split_hash": "<sha256 of sorted(train) + sorted(val) + sorted(test)>"
}
```

#### Split Hash Algorithm

The `split_hash` field MUST be computed using the following deterministic algorithm:

```python
import hashlib
import numpy as np

def compute_split_hash(train_indices, val_indices, test_indices):
    """Compute SHA-256 of sorted index arrays concatenated as int64 bytes."""
    parts = []
    for indices in [train_indices, val_indices, test_indices]:
        arr = np.array(sorted(indices), dtype=np.int64)
        parts.append(arr.tobytes())
    return hashlib.sha256(b"".join(parts)).hexdigest()
```

**Requirements:**
- Each index array MUST be sorted ascending before conversion
- Indices MUST be converted to `numpy.int64` (explicit dtype for cross-platform reproducibility)
- Concatenation order is always: train, val, test
- Hash function is SHA-256, output as lowercase hex digest

### 3.3 Split Invariants

The following MUST hold for every split file:

1. **No overlap:** `train ∩ val = ∅`, `train ∩ test = ∅`, `val ∩ test = ∅`
2. **Full coverage:** `len(train) + len(val) + len(test) == n_total`
3. **Valid range:** All indices in `range(0, n_total)`
4. **Deterministic:** Given the same seed and source data, the split MUST be identical
5. **Hash match:** `split_hash` matches recomputed value from index arrays

**Verification:** `python scripts/check_data_ready.py` validates all 5 invariants and exits non-zero on any failure.

### 3.4 Test-Split Access Policy

The held-out test split is accessible exclusively through the final evaluation script. The data-loading utility MUST default to `allow_test=False` and raise a `ValueError` if test indices are requested by any other script.

**Verification:** `python scripts/check_leakage.py` LT-2 (test index isolation) exits 0. Grep per-run outputs for test metric keys returns zero matches.

### 3.5 Prior-Project Split Inheritance

When this project inherits data splits from a prior project (e.g., Phase 1 → Phase 2), the following protocol applies.

#### Inheritance Procedure

1. **Archive original splits:** Copy the prior project's split files into `vendor/{{PRIOR_PROJECT}}_snapshot/splits/` with SHA-256 verification
2. **Verify hash:** Compute SHA-256 of each archived file and record in this contract or in the conversion script
3. **Derive missing splits:** If the prior project stored only train/test (no validation split), derive val from the prior train set using a deterministic method:

```python
from sklearn.model_selection import StratifiedShuffleSplit

# Derive val from prior train indices
sss = StratifiedShuffleSplit(
    n_splits=1,
    test_size={{VAL_FRACTION}},    # e.g., 0.2
    random_state={{SPLIT_SEED}},
)
train_sub_idx, val_sub_idx = next(sss.split(prior_train, y_prior_train))

# Map sub-indices back to original dataset indices
train_final = prior_train[train_sub_idx]
val_final = prior_train[val_sub_idx]
test_final = prior_test  # unchanged from prior project
```

4. **Integrity checks:** After derivation, verify:
   - No overlap between train, val, and test
   - Full coverage: `len(train) + len(val) + len(test) == n_total`
   - Stratification preserved: class distribution in val approximates train
5. **Write JSON:** Convert to the standard split JSON format (§3.2) with additional provenance fields:

```json
{
  "source": "{{PRIOR_PROJECT}}",
  "prior_commit_sha": "{{PRIOR_COMMIT_SHA}}",
  "prior_file_sha256": "{{PRIOR_FILE_HASH}}",
  "val_derivation": "StratifiedShuffleSplit(test_size={{VAL_FRACTION}}, random_state={{SPLIT_SEED}}) on prior train_indices"
}
```

6. **Script:** Implement the conversion in `scripts/convert_{{PRIOR_PROJECT}}_splits.py`. The script MUST exit non-zero if any hash verification or integrity check fails.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PRIOR_PROJECT}}` | Prior project identifier | sl_report |
| `{{PRIOR_COMMIT_SHA}}` | Git SHA of prior project snapshot | 54ada55c8bd9... |
| `{{PRIOR_FILE_HASH}}` | SHA-256 of archived split file | 769ce576cb28... |
| `{{VAL_FRACTION}}` | Fraction of prior train used for validation | 0.2 |

---

## 4) Leakage Prevention

### 4.1 Fit-on-Train Rule

All preprocessing transformations (scalers, encoders, imputers) MUST be fit exclusively on `X_train`. Validation and test sets receive only `.transform()` calls. This is non-negotiable.

**Verification:** `python scripts/check_leakage.py` LT-1 (fit isolation) and LT-3 (transform-only) exit 0.

```python
# CORRECT
pipeline.fit(X_train)
X_val = pipeline.transform(X_val)
X_test = pipeline.transform(X_test)

# WRONG — leaks val/test statistics into the fitted model
pipeline.fit(X_all)
```

### 4.2 Leakage Tripwires

Automated checks to detect leakage. Each tripwire has a unique ID for cross-referencing.

| ID | Check | What It Detects | How to Run |
|----|-------|-----------------|------------|
| LT-1 | Fit isolation | `.fit()` called on non-train data | `python scripts/check_leakage.py` |
| LT-2 | Test index isolation | Test indices loaded outside final eval script | `python scripts/check_leakage.py` |
| LT-3 | Transform-only on val/test | `.fit_transform()` called on val/test data | `python scripts/check_leakage.py` |

*(Add project-specific tripwires as needed.)*

### 4.3 Tripwire Detection Logic

Each tripwire has a precise detection mechanism. Implement these patterns in `scripts/check_leakage.py`.

#### LT-1: Fit Isolation

**Goal:** Prove that `.fit()` uses training data only — not train+val.

```python
# Fit preprocessor on train only
pp_train = build_preprocessor(X_train)
pp_train.fit(X_train)
mean_train = pp_train.named_steps["scaler"].mean_.copy()

# Fit preprocessor on train + val (simulating leakage)
X_full = pd.concat([X_train, X_val], ignore_index=True)
pp_full = build_preprocessor(X_full)
pp_full.fit(X_full)
mean_full = pp_full.named_steps["scaler"].mean_.copy()

# Means MUST differ — if identical, val may be leaking into fit
assert not np.allclose(mean_train, mean_full, atol=1e-10), \
    "LT-1 FAIL: train-only fit == train+val fit"
```

**Pass condition:** Scaler statistics fitted on `X_train` alone differ from statistics fitted on `X_train ∪ X_val`.

#### LT-2: Test Index Isolation

**Goal:** Prove that test indices are inaccessible outside the final evaluation script.

```python
# Default load MUST NOT include test indices
split_data = load_split(splits_dir, dataset, seed, allow_test=False)
assert "test_indices" not in split_data, \
    "LT-2 FAIL: test_indices returned when allow_test=False"

# Requesting test indices MUST raise ValueError
try:
    get_test_indices(split_data)
    assert False, "LT-2 FAIL: get_test_indices() did not raise"
except ValueError:
    pass  # expected

# allow_test=True MUST return non-empty test indices
split_with_test = load_split(splits_dir, dataset, seed, allow_test=True)
assert len(split_with_test["test_indices"]) > 0, \
    "LT-2 FAIL: test_indices empty when allow_test=True"
```

**Pass condition:** `allow_test=False` hides test indices; `get_test_indices()` raises `ValueError` on hidden data; `allow_test=True` returns non-empty indices.

#### LT-3: Transform-Only on Val/Test

**Goal:** Prove that `.transform()` on val/test does not re-fit the preprocessor.

```python
# Fit on train, then transform val
preprocessor.fit(X_train)
preprocessor.transform(X_val)

n_samples = preprocessor.named_steps["scaler"].n_samples_seen_
assert n_samples == len(X_train), \
    f"LT-3 FAIL: n_samples_seen_={n_samples}, expected {len(X_train)}"

# Transform val again — n_samples_seen_ MUST NOT change
preprocessor.transform(X_val)
n_after = preprocessor.named_steps["scaler"].n_samples_seen_
assert n_after == n_samples, \
    f"LT-3 FAIL: n_samples_seen_ changed after transform ({n_samples} -> {n_after})"
```

**Pass condition:** `n_samples_seen_` equals `len(X_train)` after fitting and remains unchanged after `.transform(X_val)`.

#### LT-4: Prediction Consistency (Optional)

> **Note:** This tripwire is optional and SHOULD be skipped for models with stochastic inference
> (e.g., MC dropout, variational methods). It is NOT a gate blocker — include only when
> deterministic inference is expected.

**Goal:** Verify that predictions are deterministic given the same fitted model and input.

```python
pred_1 = model.predict(X_val)
pred_2 = model.predict(X_val)
assert np.array_equal(pred_1, pred_2), \
    "LT-4 FAIL: predictions differ on identical input"
```

**Pass condition:** Two sequential predictions on the same input produce identical results.

*(Add project-specific tripwires below this line.)*

### 4.4 When to Run Leakage Checks

- After any change to preprocessing code
- Before starting any experiment phase
- At every phase gate
- Before final delivery

---

## 5) Dataset-Specific Preprocessing

### {{DATASET_1_NAME}}

| Step | Transformer | Parameters | Notes |
|------|-------------|------------|-------|
| *(e.g.)* | StandardScaler | default | Fit on train only |
| *(e.g.)* | OneHotEncoder | handle_unknown="ignore" | Fit on train only |
| *(e.g.)* | SimpleImputer | strategy="median" | Fit on train only |

**Feature count after preprocessing:** {{DATASET_1_FEATURES}}

### {{DATASET_2_NAME}}

| Step | Transformer | Parameters | Notes |
|------|-------------|------------|-------|
| *(e.g.)* | StandardScaler | default | Fit on train only |

**Feature count after preprocessing:** {{DATASET_2_FEATURES}}

*(Repeat for additional datasets.)*

---

## 6) EDA & Preprocessing Compatibility

If this project builds on a prior project (e.g., Phase 1 → Phase 2), EDA and preprocessing MUST be consistent unless changes are disclosed and justified.

**Verification:** Compare `outputs/eda/` summaries with prior project. If identical, REPRO document includes no-change confirmation (§6.1). If different, change disclosure template (§6.2) is completed.

### 6.1 No-Change Confirmation

If EDA and preprocessing are identical to the prior project, the REPRO document MUST include an explicit confirmation statement:

> *"EDA and preprocessing are identical to {{PRIOR_PROJECT}} for all datasets. No changes were made to feature engineering, scaling, encoding, imputation, or target encoding."*

This statement is required even when nothing changed — silence is not confirmation.

### 6.2 Change Disclosure Template

If any EDA or preprocessing differs from the prior project, each change MUST be documented using this template:

| Field | Value |
|-------|-------|
| **Change** | *(What changed — e.g., "Added binary indicator detection to preprocessing pipeline")* |
| **Rationale** | *(Why — e.g., "Binary columns were being scaled, distorting 0/1 values")* |
| **Impact on comparison** | *(How this affects cross-project comparability — e.g., "Feature dimensions differ; prior results not directly comparable")* |
| **Artifacts regenerated** | *(Which outputs were re-run — e.g., "All EDA summaries, all experiment runs")* |
| **Contract commit** | *(CONTRACT_CHANGE commit SHA)* |

### 6.3 Audit Artifact

EDA summaries MUST be generated and stored at `outputs/eda/{{DATASET_NAME}}_eda_summary.json` for each dataset. These summaries enable automated comparison with prior project summaries.

---

## 7) Data Provenance & Audit Artifacts

### 7.1 Required Artifacts

| Artifact | Path | Contents |
|----------|------|----------|
| Raw data hashes | `outputs/eda/raw_hashes.json` | SHA-256 of each raw data file |
| EDA summary | `outputs/eda/{{DATASET_NAME}}_eda_summary.json` | Row count, feature count, class distribution, missing values |
| Split labels | `outputs/eda/{{DATASET_NAME}}_split_labels.json` | Class distribution per split |

### 7.2 File Layout

```
data/
+-- raw/                    # Raw data files (gitignored)
|   +-- {{DATASET_1_FILE}}
|   +-- {{DATASET_2_FILE}}
+-- splits/                 # Split index files (committed)
|   +-- {{DATASET_1_NAME}}/
|   |   +-- split_seed{{SEED}}.json
|   +-- {{DATASET_2_NAME}}/
|       +-- split_seed{{SEED}}.json
+-- processed/              # Processed data (gitignored)
```

---

## 8) Acceptance Tests (Phase Gate)

Before proceeding to experiments, the following MUST pass:

- [ ] Raw data files present at canonical paths
- [ ] SHA-256 hashes match recorded values
- [ ] Split JSON files pass all invariants (§3.3)
- [ ] Leakage tripwires pass (§4.2)
- [ ] EDA summaries generated and consistent with prior work (if applicable)
- [ ] Preprocessing pipeline produces expected feature counts

---

## 9) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit and MUST be logged in `CHANGELOG.md`:

- Dataset filenames or paths
- Split definitions (indices, ratios, seed)
- Preprocessing pipeline (scaling, encoding, imputation, step order)
- Target variable or label mapping
- Feature handling (selection, engineering, dropped features)
- Missing-value strategy
- Class-weight or resampling strategy
- Test-access enforcement rules
- Leakage tripwire definitions
