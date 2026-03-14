# TEST ARCHITECTURE

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §3-4 for split invariants and leakage rules that tests enforce
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §2 for budget constraints validated by tests
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §7 for sanity check expectations
- See [CONFIGURATION_SPEC](CONFIGURATION_SPEC.tmpl.md) §5 for scoring metric test enforcement

**Downstream (depends on this contract):**
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §7 for test suite execution commands
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for phase gates that require passing tests

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{TEST_DIR}}` | Test directory path | `tests/` |
| `{{DATASET_N_NAME}}` | Dataset name | Adult Income |
| `{{DATASET_N_COLUMNS}}` | Column list or count for synthetic fixtures | 15 columns: age, workclass, ... |
| `{{DATASET_N_ROWS}}` | Row count for synthetic data | 200 (train) + 50 (val) |
| `{{MIN_COVERAGE_UNIT}}` | Minimum unit test coverage target | 80% of core modules |
| `{{MIN_COVERAGE_CONTRACT}}` | Minimum contract test count | 1 test per MUST requirement |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This document defines the testing philosophy, test categories, fixture patterns, and coverage expectations for the **Adversarial ML on Network Intrusion Detection** project. It ensures that governance contracts are enforced by executable tests, not just documentation.

**Core principle:** Every MUST requirement in the project contracts should have a corresponding test. If a requirement cannot be tested, downgrade it to SHOULD or design a verification method.

---

## 2) Test Categories

Tests are organized into categories that map to governance concerns. Each category has a purpose, typical test patterns, and the contracts it enforces.

| Category | Purpose | Contracts Enforced | Marker |
|----------|---------|-------------------|--------|
| **Leakage** | Prevent data leakage between splits | DATA_CONTRACT §4 | `leakage` |
| **Determinism** | Ensure reproducibility with same seed | ENVIRONMENT_CONTRACT §8 | `determinism` |
| **Sanity** | Validate pipeline credibility | METRICS_CONTRACT §7 | `sanity` |
| **Integration** | Test end-to-end script execution | SCRIPT_ENTRYPOINTS_SPEC §3-5 | `integration` |
| **Artifact** | Verify output schemas and integrity | ARTIFACT_MANIFEST_SPEC §3-5 | `artifact` |
| **Configuration** | Validate config values and constraints | CONFIGURATION_SPEC §5-6 | `config` |

### 2.1 Leakage Tests

Enforce DATA_CONTRACT §4 leakage prevention rules. These are the highest-priority tests — a leakage failure invalidates all downstream results.

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| LT-1 | Fit isolation | Preprocessor fitted on train only; fit on train differs from fit on train+val |
| LT-2 | Test access enforcement | `allow_test=False` raises `ValueError` when test indices requested |
| LT-3 | Transform-only on val/test | `.fit_transform()` on val/test raises error or produces same result as `.transform()` |
| *(add project-specific)* | | |

```python
# Example: LT-2 test access enforcement
def test_test_access_blocked_by_default():
    """Test indices must not be accessible outside final_eval."""
    with pytest.raises(ValueError, match="test"):
        load_split(dataset="adult", seed=42, allow_test=True)
```

### 2.2 Determinism Tests

Enforce ENVIRONMENT_CONTRACT §8. Same seed + same data + same code = identical outputs.

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| DT-1 | Seeded initialization | Two inits with same seed produce identical `state_dict` |
| DT-2 | Forward-pass equality | Same input + same weights → identical output within tolerance (1e-6) |
| DT-3 | Full run reproducibility | Two runs with same seed produce identical `metrics.csv` |
| *(add project-specific)* | | |

### 2.3 Sanity Tests

Enforce METRICS_CONTRACT §7. Validate that the pipeline produces sensible results before trusting experiment outputs.

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| SN-1 | Dummy baseline | Accuracy ≈ majority class proportion; F1 ≈ 0 for minority |
| SN-2 | Shuffled labels | Performance ≈ random chance; model cannot learn from noise |
| SN-3 | Overfitting check | Model can overfit a tiny dataset (confirms learning is possible) |
| *(add project-specific)* | | |

### 2.4 Integration Tests

Test end-to-end script execution with synthetic data. These tests run actual scripts but with small synthetic datasets to verify the full pipeline.

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| INT-1 | Script exits 0 | Each script completes without errors on synthetic data |
| INT-2 | Output schema | Required files exist with expected keys/columns |
| INT-3 | Budget enforcement | Scripts respect budget caps; over-budget flag set correctly |
| *(add project-specific)* | | |

### 2.5 Artifact Integrity Tests

Enforce ARTIFACT_MANIFEST_SPEC §3-5. Verify that outputs are complete, correctly hashed, and follow naming conventions.

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| AI-1 | Run manifest completeness | Every run directory has `run_manifest.json` |
| AI-2 | Hash integrity | Recomputed SHA-256 matches recorded hashes |
| AI-3 | Figure/table existence | All required artifacts present in `outputs/` |
| *(add project-specific)* | | |

### 2.6 Configuration Tests

Enforce CONFIGURATION_SPEC §5-6. Validate that config values are consistent and that the scoring metric matches the code.

| Test ID | What It Checks | Expected Behavior |
|---------|---------------|-------------------|
| CF-1 | Scoring metric match | Config metric name matches function called in code |
| CF-2 | Cross-part budget equality | Linked parts have identical budgets |
| CF-3 | Required keys present | All required config keys are non-null |
| *(add project-specific)* | | |

---

## 3) Synthetic Fixture Pattern

Tests MUST NOT depend on real datasets for unit and integration testing. Use synthetic fixtures that match the real data schema.

### 3.1 Conftest Architecture

Place shared fixtures in `{{TEST_DIR}}/conftest.py`:

```python
import numpy as np
import pandas as pd
import pytest

RNG_SEED = 42

def _make_synthetic_df(columns: dict, n_rows: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate a synthetic DataFrame matching a real dataset's column types."""
    data = {}
    for col, spec in columns.items():
        if spec["dtype"] == "float64":
            data[col] = rng.normal(spec.get("mean", 0), spec.get("std", 1), n_rows)
        elif spec["dtype"] == "int64":
            data[col] = rng.integers(spec.get("low", 0), spec.get("high", 10), n_rows)
        elif spec["dtype"] == "object":
            categories = spec.get("categories", ["a", "b", "c"])
            data[col] = rng.choice(categories, n_rows)
    return pd.DataFrame(data)


@pytest.fixture
def synthetic_train_val():
    """Return (train_df, val_df) with synthetic data matching real schema."""
    rng = np.random.default_rng(RNG_SEED)
    # Define columns matching {{DATASET_1_NAME}} schema:
    columns = {
        # "column_name": {"dtype": "float64", "mean": 38.5, "std": 13.2},
        # ... (fill in from DATA_CONTRACT)
    }
    full = _make_synthetic_df(columns, n_rows={{DATASET_1_ROWS}}, rng=rng)
    split = int(0.8 * len(full))
    return full.iloc[:split], full.iloc[split:]
```

### 3.2 Split Fixture Pattern

Generate valid split JSON files matching DATA_CONTRACT §3.2 schema:

```python
import hashlib, json

@pytest.fixture
def synthetic_split(tmp_path):
    """Create a valid split file with proper hash."""
    rng = np.random.default_rng(RNG_SEED)
    indices = rng.permutation(500)
    train = sorted(indices[:300].tolist())
    val = sorted(indices[300:400].tolist())
    test = sorted(indices[400:].tolist())

    raw = np.array(train + val + test, dtype=np.int64).tobytes()
    split_hash = hashlib.sha256(raw).hexdigest()

    split_data = {
        "dataset": "synthetic",
        "seed": RNG_SEED,
        "n_total": 500,
        "n_train": 300, "n_val": 100, "n_test": 100,
        "train_indices": train, "val_indices": val, "test_indices": test,
        "split_hash": split_hash,
    }
    path = tmp_path / "split_seed42.json"
    path.write_text(json.dumps(split_data))
    return split_data, path
```

### 3.3 Key Principles

- **Match real column types:** Synthetic data MUST have the same column names, dtypes, and approximate ranges as real data
- **Use fixed seeds:** All synthetic generation uses a fixed seed for test determinism
- **Stay small:** Synthetic datasets should be small (100-500 rows) for fast tests
- **No real data in tests:** Unit and integration tests MUST NOT require real dataset files

### 3.4 C/C++ Synthetic Fixtures (Optional)

> **Activation:** Include when the project uses C/C++ with test frameworks like Check, Google Test,
> or Catch2. Delete if not applicable.

#### Test Framework Integration

| Framework | Fixture Pattern | Example |
|-----------|----------------|---------|
| **Google Test** | `TEST_F` with fixture class | `class BenchFixture : public ::testing::Test` |
| **Catch2** | `SECTION` blocks with shared setup | `TEST_CASE("barrier") { SECTION("2 threads") { ... } }` |
| **Check** | `START_TEST` / `END_TEST` with `tcase_add_test` | `START_TEST(test_race) { ... } END_TEST` |
| **Custom** | `setup()` / `teardown()` functions | Per-test memory allocation and cleanup |

#### Conftest Pattern (C)

```c
// tests/test_utils.h — Shared test utilities
#ifndef TEST_UTILS_H
#define TEST_UTILS_H

#include <stdlib.h>
#include <string.h>

// Deterministic synthetic input generation
static inline int* make_synthetic_array(size_t n, unsigned seed) {
    int* arr = malloc(n * sizeof(int));
    srand(seed);
    for (size_t i = 0; i < n; i++) {
        arr[i] = rand() % 10000;
    }
    return arr;
}

// Fixed test seed
#define TEST_SEED 42
#define SMALL_N 100
#define MEDIUM_N 1000

#endif // TEST_UTILS_H
```

#### Performance Regression Tests

For systems projects, include performance regression tests that fail if a change degrades performance beyond a threshold:

| Test ID | What It Checks | Threshold | Action on Failure |
|---------|---------------|-----------|-------------------|
| PERF-1 | Latency regression | Median > 110% of baseline | Fail CI; investigate |
| PERF-2 | Memory regression | Peak RSS > 110% of baseline | Fail CI; investigate |
| PERF-3 | Throughput regression | Ops/sec < 90% of baseline | Warn; review |

**Rule:** Performance baselines MUST be committed to version control (e.g., `tests/baselines/perf_baseline.json`). Baselines are updated only via explicit `BASELINE_UPDATE` commits.

---

## 4) Marker-Based Test Skipping

Use pytest markers to separate tests that require real data from those that run on synthetic fixtures.

### 4.1 Marker Definitions

```python
# conftest.py or pyproject.toml
# Register custom markers:
#   data_required: marks tests that need real datasets (skip in CI)
#   slow: marks tests that take >10 seconds
```

### 4.2 Running Tests

```bash
# Run all tests except those requiring real data:
python -m pytest {{TEST_DIR}}/ -v -m "not data_required"

# Run only data-required tests (when real data is available):
python -m pytest {{TEST_DIR}}/ -v -m "data_required"

# Run a specific category:
python -m pytest {{TEST_DIR}}/ -v -m "leakage"

# Run all tests:
python -m pytest {{TEST_DIR}}/ -v
```

### 4.3 CI/CD Integration

In environments without real datasets (CI pipelines, reviewer machines), tests marked `data_required` are automatically skipped. All other tests MUST pass on synthetic data alone.

---

## 5) Test File Organization

```
{{TEST_DIR}}/
├── conftest.py                    # Shared synthetic fixtures
├── test_leakage_tripwires.py      # LT-1, LT-2, LT-3
├── test_determinism.py            # DT-1, DT-2, DT-3
├── test_sanity_checks.py          # SN-1, SN-2, SN-3
├── test_splits.py                 # Split invariants, seed decoupling
├── test_preprocessing.py          # Preprocessing pipeline correctness
├── test_config.py                 # CF-1, CF-2, CF-3 (scoring metric, budgets)
├── test_scripts.py                # INT-1, INT-2, INT-3 (end-to-end)
├── test_artifact_manifest.py      # AI-1, AI-2, AI-3
├── test_outputs.py                # Output schema validation (data_required)
└── test_{{PART_NAME}}.py          # Per-part experiment-specific tests
```

**Naming convention:** `test_<module_or_concern>.py` with test functions named `test_<what_it_checks>`.

---

## 6) Coverage Expectations

| Category | Minimum Expectation |
|----------|-------------------|
| **Leakage** | One test per tripwire defined in DATA_CONTRACT §4.2 |
| **Determinism** | At least one seeded-init and one full-run reproducibility test |
| **Sanity** | Dummy baseline + shuffled labels per dataset |
| **Integration** | At least one end-to-end test per script entrypoint |
| **Artifact** | Schema validation for every required output file |
| **Configuration** | Scoring metric match + all cross-part constraints |
| **Unit** | {{MIN_COVERAGE_UNIT}} |
| **Contract** | {{MIN_COVERAGE_CONTRACT}} |

**Coverage priority order:** Leakage > Determinism > Sanity > Configuration > Integration > Artifact > Unit

Leakage tests are highest priority because a leakage failure silently invalidates all results. Determinism is second because non-reproducible results cannot be verified.

---

## 7) Test-Driven Contract Enforcement

Each MUST requirement in the project contracts should map to a test. Maintain this traceability table:

| Contract | Section | MUST Requirement | Test ID | Test File |
|----------|---------|-----------------|---------|-----------|
| DATA_CONTRACT | §4.1 | Fit on train only | LT-1 | `test_leakage_tripwires.py` |
| DATA_CONTRACT | §3.4 | Test access default False | LT-2 | `test_leakage_tripwires.py` |
| ENVIRONMENT_CONTRACT | §8 | Deterministic seeding | DT-1 | `test_determinism.py` |
| CONFIGURATION_SPEC | §5 | Scoring metric matches code | CF-1 | `test_config.py` |
| *(add rows per project)* | | | | |

---

## 8) Acceptance Gate

Before starting experiments, the following MUST pass:

- [ ] All leakage tests pass (`pytest -m "leakage"` exits 0)
- [ ] All determinism tests pass (`pytest -m "determinism"` exits 0)
- [ ] All config tests pass (`pytest -m "config"` exits 0)
- [ ] Synthetic fixtures match real data schema (column names, dtypes)
- [ ] Test traceability table (§7) has at least one test per MUST requirement
- [ ] `pytest -m "not data_required"` exits 0 with zero failures

---

## 9) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Adding or removing a test category
- Changing leakage tripwire definitions or expected behaviors
- Modifying synthetic fixture schemas (must stay aligned with DATA_CONTRACT)
- Changing marker definitions or skip logic
- Modifying coverage expectations
- Changing the test file organization or naming conventions
