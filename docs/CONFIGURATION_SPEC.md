# CONFIGURATION SPECIFICATION

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
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §2 for budget values that must appear in config
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for scoring metric definitions that must be config-driven
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §5 for preprocessing parameters per dataset

**Downstream (depends on this contract):**
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §2 for CLI flag resolution hierarchy
- See [ARTIFACT_MANIFEST_SPEC](ARTIFACT_MANIFEST_SPEC.tmpl.md) §3 for `config_resolved.yaml` as a required per-run file
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §5 for operator disclosures sourced from resolved config

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{CONFIG_DIR}}` | Config directory path | `config/` |
| `{{BASE_CONFIG}}` | Base config filename | `budgets.yaml` |
| `{{DATASET_CONFIG_PATTERN}}` | Dataset-specific config pattern | `backbone_{{DATASET}}.yaml` |
| `{{SCORING_METRIC}}` | Primary scoring metric name | `val_loss` |
| `{{SCORING_METRIC_DIRECTION}}` | Optimization direction | `minimize` or `maximize` |
| `{{SCORING_METRIC_FUNCTION}}` | Exact computation | `sklearn.metrics.f1_score(average='binary')` |
| `{{DEFAULT_SEED}}` | Default random seed | 42 |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This specification defines the config-as-code governance for the **Adversarial ML on Network Intrusion Detection** project. It ensures that every experiment parameter is traceable, every run is reproducible from its resolved config, and no configuration value is silently hardcoded.

**Core principle:** If a value affects experiment behavior, it lives in config — not in code.

---

## 2) Configuration Hierarchy

Config values are layered, with each level overriding the one below. The fully resolved result is dumped per run.

```
┌─────────────────────────────────────────────────┐
│  CLI flags                    (highest priority) │
├─────────────────────────────────────────────────┤
│  Component-specific config     (method/algo)     │
├─────────────────────────────────────────────────┤
│  Dataset-specific config       (per dataset)     │
├─────────────────────────────────────────────────┤
│  Base config                   (project-wide)    │
├─────────────────────────────────────────────────┤
│  Hardcoded defaults            (lowest priority) │
└─────────────────────────────────────────────────┘
                    ↓
        config_resolved.yaml  (per-run dump)
```

### Resolution Rule

When the same key appears at multiple levels:

1. **CLI flag** — highest priority; always wins
2. **Component config** — method-specific overrides (e.g., optimizer-specific learning rates)
3. **Dataset config** — per-dataset values (e.g., input dimensions, class counts)
4. **Base config** — project-wide defaults (e.g., budgets, seeds, eval intervals)
5. **Hardcoded default** — lowest priority; used only when no config specifies the value

**Ambiguity rule:** If a value's source is unclear, the `config_resolved.yaml` dump is the source of truth for what the run actually used.

---

## 3) Config File Layout

```
{{CONFIG_DIR}}/
├── {{BASE_CONFIG}}                    # Project-wide: budgets, seeds, thresholds
├── {{DATASET_CONFIG_PATTERN}}         # Per-dataset: input dims, class count, architecture
├── *(component-specific configs)*     # Per-method overrides (if needed)
└── *(baseline/provenance configs)*    # Prior-project baselines (if applicable)
```

### Base Config (`{{BASE_CONFIG}}`)

The base config MUST contain at minimum:

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `seeds.default` | int | Default random seed | `42` |
| `seeds.stability_list` | list[int] | Seeds for multi-seed runs | `[42, 123, 456, 789, 1024]` |
| `partN.budget` | int | Compute budget per experimental part | `10000` |
| `partN.eval_interval_steps` | int | Steps between metric evaluations | `50` |
| `scoring_metric` | str | Primary metric name (see §5) | `val_loss` |
| `scoring_direction` | str | Optimization direction | `minimize` |

*(Add project-specific keys. Every key MUST have a comment explaining its source and rationale.)*

### Dataset Config (`{{DATASET_CONFIG_PATTERN}}`)

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `input_dim` | int | Feature count after preprocessing | `104` |
| `n_classes` | int | Number of target classes | `2` |
| `hidden_sizes` | list[int] | Model architecture layers | `[100]` |
| `activation` | str | Activation function | `relu` |

*(Add project-specific keys. Architecture values MUST match DATA_CONTRACT §5 preprocessing output dimensions.)*

---

## 4) Resolved Config Dump

Every experiment run MUST write a `config_resolved.yaml` to its output directory. This file captures the **fully resolved** configuration — the exact values the run used, after all layers are merged.

### Requirements

- MUST include every parameter that affects run behavior
- MUST be written before the run begins (not reconstructed after)
- MUST be included in the per-run manifest hash (see ARTIFACT_MANIFEST_SPEC §3)
- MUST be human-readable YAML (not binary or minified)

### Required Fields

```yaml
# config_resolved.yaml — auto-generated, do not edit
run_id: "{{RUN_ID}}"
timestamp_utc: "2026-01-01T00:00:00Z"
git_sha: "abc123..."

# Seeds
seed: 42

# Budget
budget_type: "grad_evals"       # or "func_evals"
budget_value: 10000
eval_interval_steps: 50

# Scoring
scoring_metric: "{{SCORING_METRIC}}"
scoring_direction: "{{SCORING_METRIC_DIRECTION}}"

# Dataset
dataset: "adult"
input_dim: 104
n_classes: 1

# Method
method: "adam"
# ... (all method-specific hyperparameters)

# Thresholds (if applicable)
threshold_l: 0.33

# Resolution source (which level provided each key)
_resolution_sources:
  seed: "base_config"
  budget_value: "base_config"
  input_dim: "dataset_config"
  method: "cli_flag"
```

### Resolution Source Tracking

The `_resolution_sources` block is RECOMMENDED (not required). When present, it records which config level provided each key, enabling full auditability.

---

## 5) Scoring Metric as Config (U28)

The primary scoring metric MUST be a first-class configuration value, not a hardcoded string in code.

### Config Encoding

```yaml
# In {{BASE_CONFIG}}:
scoring_metric: "{{SCORING_METRIC}}"
scoring_direction: "{{SCORING_METRIC_DIRECTION}}"

# Per-dataset overrides (if needed):
# In dataset config:
scoring_metric_function: "{{SCORING_METRIC_FUNCTION}}"
```

### Test Enforcement

Scripts MUST verify that the metric computed at runtime matches the metric declared in config. This prevents silent metric drift.

```python
# Example enforcement pattern:
resolved = load_config_resolved()
assert resolved["scoring_metric"] == "val_loss", (
    f"Scoring metric mismatch: config says '{resolved['scoring_metric']}', "
    f"but code computes 'val_loss'. Update config or code."
)
```

**Test requirements:**
- [ ] At least one test asserts that the scoring metric name in config matches the function called in code
- [ ] At least one test asserts that the scoring direction (minimize/maximize) matches the comparison operators in code
- [ ] If per-dataset metrics differ, each dataset config specifies its own metric and tests verify per-dataset

### Why This Matters

Without config-driven metrics, it is possible to:
- Report "F1" in the paper but compute "accuracy" in code
- Optimize for "minimize val_loss" but select models by "maximize accuracy"
- Change the metric without triggering a `CONTRACT_CHANGE`

Making the metric a config value with test enforcement prevents all three.

---

## 6) Config Validation

### Schema Validation

At startup, scripts SHOULD validate the resolved config against expected types and ranges:

| Key | Type | Constraint | On Failure |
|-----|------|-----------|------------|
| `seed` | int | > 0 | Fatal error |
| `budget_value` | int | > 0 | Fatal error |
| `eval_interval_steps` | int | > 0, divides budget evenly | Warning |
| `scoring_metric` | str | Non-empty | Fatal error |
| `scoring_direction` | str | `minimize` or `maximize` | Fatal error |
| `input_dim` | int | > 0 | Fatal error |
| `n_classes` | int | ≥ 1 | Fatal error |

*(Add project-specific validation rules.)*

### Cross-Part Consistency

Where experimental parts share constraints (e.g., Part 3 budget MUST equal Part 2 budget), validation MUST check cross-part equality at Phase 0:

```python
assert config["part3"]["budget"] == config["part2"]["budget"], (
    f"Cross-part budget mismatch: part2={config['part2']['budget']}, "
    f"part3={config['part3']['budget']}"
)
```

---

## 7) Config Comments & Rationale

Every config value MUST include a comment documenting:

1. **What it is** — brief description
2. **Source** — which authority document or decision justified this value
3. **Rationale** — why this specific value was chosen (not just "default")

**Good example:**

```yaml
threshold_l: 0.33   # float — fixed val-loss threshold ℓ
                     # Source: EXPERIMENT_CONTRACT §5
                     # Rationale: derived from Adam baseline (seed 42):
                     # best_val_loss=0.3129; 0.33 is reachable by all
                     # momentum/Adam variants but not plain SGD
```

**Bad example:**

```yaml
threshold_l: 0.33   # threshold
```

---

## 8) Forbidden Patterns

### No Hardcoded Magic Numbers

```python
# WRONG — budget buried in code
for step in range(10000):
    ...

# CORRECT — budget from config
for step in range(config["budget_value"]):
    ...
```

### No Implicit Defaults

```python
# WRONG — default hidden in function signature
def build_model(hidden=100):
    ...

# CORRECT — default in config, passed explicitly
def build_model(hidden_sizes: list[int]):
    ...
```

### No Config-Code Divergence

If a config key exists but the code ignores it, that is a bug. Every config key MUST be consumed by the code, and every tunable parameter in the code MUST come from config.

---

## 9) Acceptance Gate

Before starting experiments, the following MUST pass:

- [ ] All config files present in `{{CONFIG_DIR}}/`
- [ ] Base config has all required keys (seeds, budgets, scoring metric)
- [ ] Dataset configs match DATA_CONTRACT preprocessing dimensions
- [ ] Cross-part budget constraints verified
- [ ] Scoring metric config matches code (test passes)
- [ ] Config comments include source and rationale for every value
- [ ] `config_resolved.yaml` is produced on a test run

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit and re-running all impacted experiments:

- Any value in `{{BASE_CONFIG}}` (budgets, seeds, thresholds, eval intervals)
- Any value in dataset configs (architecture, input dimensions, class counts)
- Scoring metric name, direction, or computation function
- Config resolution hierarchy or merge rules
- Adding or removing a config key
- Changing config file layout or naming conventions
- Changing `config_resolved.yaml` schema
