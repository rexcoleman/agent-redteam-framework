# METRICS & EVALUATION CONTRACT

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §2 for canonical dataset paths and §5 for preprocessing

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §5 for evaluation rules and metric logging
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §4 for summary table column definitions
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) §5 for baseline comparison requirements
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §4 for sanity check scripts

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{DATASET_N_NAME}}` | Dataset name | Dataset A |
| `{{DATASET_N_TASK}}` | Task type | binary classification |
| `{{DATASET_N_PRIMARY_METRICS}}` | Required primary metrics | Accuracy + F1 (binary) |
| `{{DATASET_N_METRIC_FUNCTION}}` | Exact sklearn/torch call | `f1_score(average='binary', pos_label=1)` |
| `{{OPTIMIZATION_OBJECTIVE}}` | What experiments minimize/maximize | validation loss |
| `{{THRESHOLD_DEFINITION}}` | How convergence threshold is defined | Derived from baseline run |
| `{{SANITY_CHECKS}}` | Required sanity baselines | Dummy classifier, shuffled labels |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines how metrics are computed, thresholds are set, and evaluation results are validated for the **Adversarial ML on Network Intrusion Detection** project.

---

## 2) Dataset / Task Mapping & Mandatory Metrics

| Dataset | Task | Primary Metrics | Computation |
|---------|------|-----------------|-------------|
| {{DATASET_1_NAME}} | {{DATASET_1_TASK}} | {{DATASET_1_PRIMARY_METRICS}} | {{DATASET_1_METRIC_FUNCTION}} |
| {{DATASET_2_NAME}} | {{DATASET_2_TASK}} | {{DATASET_2_PRIMARY_METRICS}} | {{DATASET_2_METRIC_FUNCTION}} |

**Rules:**
- Primary metrics are non-negotiable. They MUST appear in every summary and the final evaluation.
- Additional metrics may be reported if justified and consistent, but MUST NOT replace primary metrics.
- All metric computations MUST be centralized in a single module to prevent inconsistent calls.

**Verification:** Assert primary metric keys exist in every `summary.json` and `final_eval_results.json`. Grep codebase for metric computation calls — all MUST import from the centralized module.

---

## 3) Primary Optimization Objective

All experiments optimize: **{{OPTIMIZATION_OBJECTIVE}}**

*(e.g., "validation loss" — all parts use validation loss as the objective for comparisons, hyperparameter selection, and convergence analysis.)*

---

## 4) Prediction Conventions

### Classification Threshold

- **Default threshold:** 0.5 for binary classification
- If a non-default threshold is used, it MUST be justified, logged in `config_resolved.yaml`, and disclosed in the report

### Positive Class Convention

*(For binary classification: define which class is positive and the label mapping.)*

| Label | Value | Description |
|-------|-------|-------------|
| *(e.g.)* Negative | 0 | *(e.g.)* Income <=50K |
| *(e.g.)* Positive | 1 | *(e.g.)* Income >50K |

---

## 5) Convergence Threshold Governance

*(If your project uses a convergence threshold for time-to-threshold comparisons. Delete this section if not applicable.)*

### 5.1 Definition

- **Symbol:** ℓ (or equivalent)
- **Derivation:** {{THRESHOLD_DEFINITION}}
- **Lock rule:** The threshold MUST be defined once and used consistently across all comparable experiments. Changing it after experiments begin requires a `CONTRACT_CHANGE`.

**Verification:** `git log` for budget config edits after threshold lock. Assert `threshold_l` value is identical across all `config_resolved.yaml` files that reference it.

### 5.2 Setting Procedure (Test-Safe)

ℓ MUST be derived without any access to test data:

1. Run the baseline method with the default seed for the full compute budget
2. Record the best validation loss achieved at a fixed budget percentile (e.g., 50% or 75%)
3. Choose ℓ such that it provides **discriminative signal**: reachable by the baseline within budget but challenging enough that weaker methods may not reach it
4. Document the chosen ℓ value and rationale in the report Methods section
5. Lock ℓ in the budget config file (e.g., `part2.threshold_l` in `{{BUDGET_CONFIG_FILE}}`)

### 5.3 Logging Requirements

For every method × seed run, log in `summary.json`:

| Field | Type | Description |
|-------|------|-------------|
| `steps_to_l` | int/null | Steps to first reach metric ≤ ℓ; null if not reached |
| `wall_clock_to_l` | float/null | Wall-clock seconds to first reach ℓ; null if not reached |
| `reached_l` | bool | Whether ℓ was reached within the budget |

### 5.4 Unreachable ℓ Handling

- If a method does not reach ℓ within budget, log `reached_l: false`
- In the summary table, report "—" or "not reached" for Time to ℓ
- DO NOT exclude these runs from the comparison — failure to reach ℓ is informative
- In the report, discuss WHY certain methods failed to reach ℓ and attribute causes (divergence, plateaus, insufficient capacity, etc.)

---

## 6) Generalization Gap

The generalization gap is defined as:

```
gen_gap = train_loss - val_loss  (at budget endpoint)
```

*(Or use your preferred definition.)*

- MUST be computed for every experiment run
- MUST be logged in `summary.json`
- MUST be discussed in the report for each experimental part

---

## 7) Sanity Check Protocol

Sanity checks MUST be run before main experiments to establish pipeline credibility.

### 7.1 Required Checks

| Check | Expected Behavior | Failure Implies | Script |
|-------|-------------------|-----------------|--------|
| **Dummy baseline** | Accuracy ≈ majority class proportion; F1 ≈ 0 for minority class | Label encoding error or data corruption | `scripts/run_sanity_checks.py` |
| **Shuffled labels** | Performance collapses to approximately chance level | Data leakage or pipeline bug | `scripts/run_sanity_checks.py` |
| *(Optional)* Train/test swap | Performance degrades or is comparable | Confirms distribution similarity | `scripts/run_sanity_checks.py` |
| *(Add project-specific)* | | | |

### 7.2 Credibility Gate

- Sanity checks MUST be produced and recorded BEFORE main experiments begin
- If dummy or shuffled-label results are anomalous (e.g., shuffled F1 substantially above chance), MUST investigate and fix before proceeding
- Experiment results produced without passing sanity checks are not credible

**Verification:** `ls outputs/sanity_checks/` confirms expected JSON files exist. Dummy accuracy ≈ majority proportion; shuffled F1 ≈ chance level. Git log confirms sanity check commit precedes experiment commits.

### 7.3 Logging

Sanity check outputs MUST be:
- Stored at `outputs/sanity_checks/{{CHECK_NAME}}_{{DATASET}}.json`
- Recorded in the artifact manifest
- Included in the report text or appendix
- Command: `python scripts/run_sanity_checks.py --dataset {{DATASET_NAME}} --seed {{DEFAULT_SEED}}`

---

## 8) Summary Table Interface

The summary table (T1) MUST include these columns at minimum:

| Column | Description |
|--------|-------------|
| Method | Algorithm/optimizer/technique name |
| Best Val Loss | Lowest validation loss achieved |
| Test Metric | Primary test metric (from final eval only) |
| Time to ℓ | Steps/evals to reach threshold ℓ (if applicable) |
| Budget Used | Gradient evals, function evals, or equivalent |
| Notes | Over-budget flag, architecture changes, etc. |

- SL/prior baseline row MUST be included if applicable
- Over-budget runs MUST be marked and excluded from head-to-head claims
- Dispersion (median + IQR) MUST be shown for seed-aggregated results

---

## 9) Logging Schema

Every experiment run MUST log metrics in a consistent schema.

### Per-step logging (`metrics.csv`)

| Field | Type | Description |
|-------|------|-------------|
| step | int | Step/eval/epoch number |
| train_loss | float | Training loss at this step |
| val_loss | float | Validation loss at this step |
| val_metric_1 | float | Primary validation metric |
| wall_clock_s | float | Cumulative wall-clock seconds |
| *(add fields)* | | |

### Per-run summary (`summary.json`)

| Field | Type | Description |
|-------|------|-------------|
| dataset | str | Dataset name |
| method | str | Method/algorithm name |
| seed | int | Random seed used |
| best_val_loss | float | Best validation loss |
| budget_used | dict | `{grad_evals: N, func_evals: M}` |
| over_budget | bool | Whether budget was exceeded |
| gen_gap | float | Generalization gap at budget endpoint |
| steps_to_l | int/null | Steps to reach threshold ℓ |
| reached_l | bool | Whether ℓ was reached |
| *(add fields)* | | |

---

## 10) Per-Class Behavior Reporting

For multiclass tasks, aggregate metrics (accuracy, macro-F1) can mask severe failures on tail classes. This section prevents that.

### 10.1 When Required

Per-class reporting is REQUIRED when:
- The task is multiclass (3+ classes)
- Class imbalance exists (any class < 10% of total samples)
- The project specification explicitly requires per-class analysis

### 10.2 What to Report

| Artifact | Contents | Format |
|----------|----------|--------|
| Per-class F1 | F1 score for each class | `per_class_f1` dict in `summary.json` |
| Confusion matrix | Full N×N matrix | Figure or table in report |
| Per-class discussion | Analysis of which classes succeed/fail and why | Report text (human-written) |

### 10.3 Rule

DO NOT silently average away tail-class failures. If a method achieves high macro-F1 but fails completely on one class, this MUST be discussed. The report MUST include a per-class breakdown for at least one representative run.

**Verification:** `per_class_f1` dict present in `summary.json` for multiclass datasets. Report text contains per-class discussion (search for "per-class" or class names).

---

## 11) Budget-Matched Claims Rule

Claims comparing methods MUST use budget-matched evidence.

### 11.1 Requirements

- Make comparative claims ONLY when all compared methods ran with identical budgets
- Include dispersion (median + IQR or mean ± std) — not just point estimates
- Explain failures (divergence, plateaus, oscillation) and attribute causes
- DO NOT compare methods run at different budgets in head-to-head tables or claims

**Verification:** Parse `summary.json` across methods within each part; assert `budget_allocated` values are equal. Summary table includes dispersion columns.

### 11.2 Over-Budget Exclusion

- Over-budget runs MUST set `over_budget: true` in `summary.json`
- Over-budget runs MUST be marked with a flag in the summary table
- Over-budget runs MUST be excluded from head-to-head comparison claims
- Over-budget runs MAY appear in supplementary analysis with clear disclosure

### 11.3 Seed Aggregation

- Single-seed results are not sufficient for comparative claims
- Report median + IQR across the seed list (preferred) or mean ± std
- When reporting means, also report the number of seeds and the stability seed list

---

## 12) Delta Reporting

When an experiment part builds on a prior part (e.g., regularization study builds on optimizer selection), report the explicit delta.

### 12.1 Format

```
Δ(Metric) = Current_Part_value − Baseline_Part_value
```

- Example: `Δ(Test F1) = Part3_best_combo − Part2_Adam_baseline = +0.023`
- Include deltas in both the summary table and report text
- Compute deltas under identical budgets, seeds, and evaluation conditions

### 12.2 Baseline Reference

- Clearly identify which prior part run serves as the baseline
- The baseline MUST use the same budget and evaluation protocol
- Lock the baseline run ID in the configuration to prevent drift

---

## 13) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Metric definitions or computation functions
- Positive class convention or label mapping
- Classification threshold
- F1 averaging mode (binary vs macro vs weighted)
- Convergence threshold ℓ (after initial lock)
- Generalization gap definition
- Sanity check requirements
- Evaluation determinism rules
- Test-split access policy
- Logging schema fields
- Per-class reporting requirements
- Budget-matched claims policy

---

## Appendix B: Unsupervised Evaluation Menu (Optional)

> **Activation:** Include this appendix when your project involves clustering, dimensionality
> reduction, density estimation, or other unsupervised methods. Delete if not applicable.

### B.1 Clustering Metrics

| Metric | When to Use | Computation | Notes |
|--------|-------------|-------------|-------|
| **Silhouette Score** | Always (primary internal metric) | `sklearn.metrics.silhouette_score` | Range [-1, 1]; higher is better |
| **Adjusted Rand Index** | When ground-truth labels available | `sklearn.metrics.adjusted_rand_score` | Range [-0.5, 1]; corrects for chance |
| **Normalized Mutual Info** | When ground-truth labels available | `sklearn.metrics.normalized_mutual_info_score` | Range [0, 1]; robust to cluster count |
| **Davies-Bouldin Index** | Complement to silhouette | `sklearn.metrics.davies_bouldin_score` | Lower is better |
| **Inertia / SSE** | K-Means family only | Model attribute | Use for elbow analysis only; not for cross-method comparison |

### B.2 Dimensionality Reduction Metrics

| Metric | When to Use | Notes |
|--------|-------------|-------|
| **Reconstruction error** | Autoencoders, PCA | MSE between input and reconstruction |
| **Explained variance ratio** | PCA | Cumulative proportion of variance explained |
| **Trustworthiness** | Manifold methods (t-SNE, UMAP) | `sklearn.manifold.trustworthiness`; measures neighborhood preservation |
| **Continuity** | Manifold methods | Complement to trustworthiness |

### B.3 Density Estimation Metrics

| Metric | When to Use | Notes |
|--------|-------------|-------|
| **Log-likelihood** | Generative models, GMMs | On held-out validation set |
| **BIC / AIC** | Model selection | Lower is better; penalizes complexity |

### B.4 Unsupervised Sanity Checks

| Check | Expected Behavior | Failure Implies |
|-------|-------------------|-----------------|
| Random assignment baseline | Silhouette ≈ 0, ARI ≈ 0 | If model doesn't beat random, it's not finding structure |
| Shuffled features | Metrics degrade | If metrics are unchanged, features are not informative |
| Known-structure synthetic data | Algorithm recovers known clusters | Algorithm implementation error |

---

## Appendix C: RL / Sequential Policy Evaluation (Optional)

> **Activation:** Include this appendix when your project involves reinforcement learning or
> sequential decision-making. Delete if not applicable.

### C.1 Policy Evaluation Metrics

| Metric | Description | Aggregation |
|--------|-------------|-------------|
| **Mean Return** | Average cumulative reward over evaluation episodes | Mean ± std across episodes |
| **Median Return** | Median cumulative reward | Median + IQR across episodes |
| **Success Rate** | Fraction of episodes achieving goal (if applicable) | Proportion ± binomial CI |
| **Mean Episode Length** | Average steps per episode | Mean ± std |

### C.2 Evaluation Protocol

- **Evaluation frequency:** Every {{EVAL_INTERVAL_EPISODES}} training episodes
- **Evaluation episodes:** {{EVAL_EPISODES}} episodes per evaluation point
- **Policy mode:** Greedy / deterministic (no exploration noise during evaluation)
- **Environment seeds:** Fixed evaluation seed set, separate from training seeds

### C.3 Learning Curve Requirements

- Plot mean evaluation return vs training episodes (with shaded ± std band)
- Include a random-policy baseline for reference
- If multiple algorithms are compared, use identical evaluation episodes and seeds

### C.4 RL-Specific Sanity Checks

| Check | Expected Behavior | Failure Implies |
|-------|-------------------|-----------------|
| Random policy baseline | Return ≈ expected random performance | Environment or reward bug |
| Known-optimal environment | Algorithm converges to known optimal | Implementation error |
| Reward shaping verification | Shaped reward doesn't change optimal policy | Reward design error |

---

## Appendix D: Systems Sanity Checks (Optional)

> **Activation:** Include this appendix when your project involves systems programming (C/C++),
> performance benchmarking, or concurrent implementations. Delete if not applicable.

### D.1 Null Baseline

| Check | What It Measures | Expected Behavior | Failure Implies |
|-------|-----------------|-------------------|-----------------|
| **Empty loop** | Timing overhead | Latency ≈ timer resolution (< 1μs) | Timing infrastructure is broken |
| **No-op function call** | Call overhead | Latency ≈ function call overhead | Measurement code has side effects |
| **Identity copy** | Memory bandwidth baseline | Throughput ≈ STREAM benchmark for platform | Memory subsystem issue |

**Rule:** Null baseline MUST be measured before any implementation benchmark. If null baseline is anomalous (> 10× expected), investigate before proceeding.

### D.2 Zero-Overhead Test

Verify that instrumentation does not distort measurements:

| Check | Protocol | Expected | Failure Implies |
|-------|----------|----------|-----------------|
| **Timer overhead** | Measure `clock_gettime` call latency | < 100ns | Use a coarser timer or amortize |
| **Sanitizer overhead** | Compare ASan vs release build latency | ASan 2-3× slower is normal | If > 5× slower, benchmark with release profile only |
| **Assertion overhead** | Compare NDEBUG vs debug build | Assertions should be < 5% overhead | Assertions in hot path — guard with `#ifndef NDEBUG` |

### D.3 Sequential Consistency Check

For concurrent implementations, verify correctness with a single thread before measuring with multiple threads:

| Check | Expected Behavior | Failure Implies |
|-------|-------------------|-----------------|
| **Single-thread correctness** | Matches reference implementation output | Algorithm bug (not concurrency bug) |
| **Deterministic with 1 thread** | Two runs produce identical output | Non-determinism in single-threaded path |
| **Monotonic scaling** | 2 threads ≥ 1 thread throughput | Synchronization overhead exceeds parallelism benefit |

### D.4 Memory Sanity

| Check | Expected Behavior | Failure Implies |
|-------|-------------------|-----------------|
| **Zero allocations in hot path** | `malloc` call count = 0 during measured region | Unexpected heap allocation |
| **No memory leaks** | Valgrind `--leak-check=full` reports zero leaks | Resource management bug |
| **Stack usage** | Stack depth < system limit | Potential stack overflow in recursion |
