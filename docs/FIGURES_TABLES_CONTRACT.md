# FIGURES & TABLES CONTRACT

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
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §5 for per-run output schemas (data sources for figures)
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §8 for summary table interface and required columns

**Downstream (depends on this contract):**
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) §4 for figure/table placement in report
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §5 for artifact generation scripts

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{FIGURE_COUNT}}` | Number of required figures | 8-10 |
| `{{TABLE_COUNT}}` | Number of required tables | 2 |
| `{{PRODUCER_SCRIPT}}` | Script that generates artifacts | scripts/make_report_artifacts.py |
| `{{FIGURE_FORMAT}}` | Output format | PDF |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines every figure and table required for the **Adversarial ML on Network Intrusion Detection** report. Each artifact has a unique ID, a data source, a producer script, and caption requirements.

---

## 2) Artifact Directories & Naming

| Type | Directory | Naming Convention |
|------|-----------|-------------------|
| Figures | `outputs/figures/` | `f{{N}}_{{short_name}}.{{FORMAT}}` |
| Tables | `outputs/tables/` | `t{{N}}_{{short_name}}.csv` |

**Producer script:** `{{PRODUCER_SCRIPT}}`

The producer script MUST:
- Be deterministic (same inputs → same outputs, byte-for-byte)
- Read from experiment outputs and `final_eval_results.json` only
- NOT re-run any training
- Generate all figures and tables in a single invocation
- Write the artifact manifest as its final step

**Verification:** Run producer script twice; compare SHA-256 hashes of all outputs. Zero differences confirms determinism. `python scripts/verify_manifests.py` exits 0.

---

## 3) Required Figures

| ID | Title | Report Section | Data Source | Key Interpretation |
|----|-------|---------------|-------------|-------------------|
| F1 | *(e.g.)* Loss vs Wall-Clock | *(e.g.)* Sec 5-7 | `metrics.csv` | *(e.g.)* Which methods converge fastest |
| F2 | *(title)* | *(section)* | *(source)* | *(what to interpret)* |
| *(add rows)* | | | | |

*(Fill in one row per required figure. Include optional figures with a note.)*

---

## 4) Required Tables

| ID | Title | Report Section | Columns | Data Source |
|----|-------|---------------|---------|-------------|
| T1 | Summary Table | *(e.g.)* Before Conclusion | Method, Best Val Loss, Test Metric, Time to ℓ, Budget, Notes | `summary.json` + `final_eval_results.json` |
| T2 | Sanity Checks | *(e.g.)* Part 2 | Check, Accuracy, F1, Expected | `sanity_checks/*.json` |
| *(add rows)* | | | | |

### Summary Table Locked Columns

The summary table MUST include these columns at minimum. Additional columns may be added but these MUST NOT be removed.

| Column | Source | Notes |
|--------|--------|-------|
| **Method** | — | Descriptive label (e.g., "P1-RHC-Adult", "P2-Adam", "Baseline") |
| **Best Val Loss** | `summary.json` → `best_val_loss` | Min val_loss over the budgeted trajectory |
| **Test Metric** | `final_eval_results.json` ONLY | Primary test metric per dataset; MUST NOT come from per-run summary |
| **Time to ℓ** | `summary.json` → `steps_to_l` | "—" if `reached_l=false` or not applicable |
| **Budget Used** | `summary.json` → `budget_used` | grad_evals, func_evals, or episodes as appropriate |
| **Notes** | — | Over-budget flag, architecture changes, etc. |

**Optional recommended columns:**
- `Test Accuracy` — required by some projects alongside the primary metric
- `Δ(Test Metric)` — delta vs baseline for improvement-tracking parts
- `Train Loss @ Budget` — enables generalization gap analysis
- `Dispersion` — IQR or ± std for seed-aggregated values

### Seed Aggregation Rule

- Report **median** across seeds (preferred) or mean
- MUST include a dispersion indicator: median ± IQR or mean ± std
- **Never report bare means without dispersion** — single-point estimates are not credible for comparative claims
- Dispersion MUST appear as adjacent columns, parenthetical notation, or footnotes

**Verification:** Inspect summary table for dispersion indicators (±, IQR, std) adjacent to every seed-aggregated value. Bare single numbers without dispersion fail this check.

### Summary Table Requirements

- [ ] Includes all methods from all experimental parts
- [ ] Includes baseline/prior-work row(s) for comparison
- [ ] Over-budget runs marked with a flag and excluded from head-to-head claims
- [ ] Dispersion shown (median + IQR) for seed-aggregated results
- [ ] Test metrics sourced exclusively from `final_eval_results.json`
- [ ] Delta column present for improvement-tracking parts (if applicable)

---

## 5) Caption Requirements

### 5.1 Figure Takeaway Rule

Every figure and table caption MUST include an **interpretive takeaway** — a sentence explaining what the result means, tied to the experiment's mechanism. DO NOT merely restate the legend or describe the data.

**Verification:** Review each caption for a sentence that explains *why* the result occurred, not just *what* it shows. Captions that only describe axes or legend entries fail this check.

| Element | Required | Description |
|---------|----------|-------------|
| **Descriptive title** | MUST | What is being shown |
| **Key parameters** | MUST | Budget, seed count, aggregation method, threshold (where applicable) |
| **Takeaway** | MUST | One interpretive sentence explaining what the result means |

**Bad caption:** "Validation loss curves for 7 optimizers."
**Good caption:** "Validation loss vs gradient evaluations for 7 optimizers on Adult (10k grad evals, 5 seeds, median shown). Adam converges 3× faster than SGD, consistent with adaptive scaling compensating for gradient magnitude variation."

### 5.2 Operator & Hyperparameter Disclosure

Method-comparison figures MUST disclose the key hyperparameters that distinguish the compared methods. Without disclosure, the reader cannot assess whether differences are due to the method or its configuration.

| Figure Type | Required Disclosures in Caption |
|-------------|-------------------------------|
| **Black-box / RO figures** | Per-algorithm operator settings (e.g., restart policy, temperature schedule, population size, mutation rate, elitism); trainable parameter count; budget (func_evals) |
| **Gradient optimizer figures** | Budget (grad_evals); learning rate; threshold ℓ value (if applicable); seed count and aggregation |
| **Regularization figures** | Budget (must match baseline); locked optimizer config from prior part; Δ annotation vs baseline |
| **Heatmap figures** | Exact grid values; which metric is displayed in cells; budget per cell |
| **Stability figures** | Seed count; aggregation method (median + IQR or mean ± std) |
| **Composition figures** | Component provenance (which prior part each component came from); phase-specific budgets |

### 5.3 Budget and Seed Annotation Rule

Every figure and table MUST indicate:
- The compute budget used (grad_evals, func_evals, episodes, or wall_clock as appropriate)
- The seed aggregation method and count
- Whether displayed values are median, mean, or individual-seed lines

### 5.4 Per-Figure Caption Checklist

*(Customize per figure. Example:)*

- **F1 (Loss vs Wall-Clock):** Budget, seed count, methods shown, which is fastest
- **F2 (RO Progress):** Algorithm settings (operator disclosures), func_eval budget, trainable param count
- **Summary Table (T1):** Column definitions, what "Test Metric" means per dataset, baseline source

---

## 6) Integration Constraints

- Figures MUST be referenced in the report text with an interpretation (not just "see Figure X")
- Each figure/table reference MUST include a takeaway sentence
- Figures MUST be placed near their first reference in the text
- Figure PDFs MUST be vector format for print quality

---

## 7) Acceptance Criteria / Exit Gate

- [ ] All required figures present in `outputs/figures/`
- [ ] All required tables present in `outputs/tables/`
- [ ] Producer script runs without errors
- [ ] Artifact manifest records SHA-256 for every figure/table
- [ ] Captions drafted with takeaways (review before delivery)
- [ ] Summary table has all required columns and rows
- [ ] Test metrics in tables match `final_eval_results.json` exactly

---

## 8) Visualization Catalog by Method Family

Use this catalog to select appropriate figure types for each experiment family. Not all figure types apply to every project — select based on your experimental parts.

### 8.1 Convergence Plots

| Figure Type | When to Use | X-Axis | Y-Axis | Annotation |
|------------|-------------|--------|--------|------------|
| Loss vs evaluations | Comparing methods at matched budgets | Budget units (grad_evals, func_evals) | val_loss | Threshold ℓ reference line |
| Loss vs wall-clock | Comparing wall-clock efficiency | wall_clock_sec | val_loss | — |
| Best-so-far objective | Black-box / RO methods | func_eval | best_val_loss | Operator settings in caption |

### 8.2 Sensitivity Analysis

| Figure Type | When to Use | Layout | Data Source |
|------------|-------------|--------|-------------|
| Hyperparameter heatmap | Sweeping 2 hyperparams on a coarse grid | 2D grid, color = metric | Heatmap CSVs |
| Learning rate sweep | Comparing LR sensitivity across methods | 1D, x=LR, y=metric | Per-LR run summaries |

### 8.3 Stability Analysis

| Figure Type | When to Use | Display | Key Rule |
|------------|-------------|---------|----------|
| Stability bands | Showing variance across seeds | Median line + IQR shading | Must use ≥ 2 seeds; single-seed results are not stability analysis |
| Box plots | Comparing final metric distributions | Per-method box | Median + quartiles + outliers |

### 8.4 Comparison Panels

| Figure Type | When to Use | Content | Key Rule |
|------------|-------------|---------|----------|
| Regularization sweep | Comparing techniques at matched budgets | Bar/point + dispersion per technique | Δ annotation vs baseline required |
| Composition comparison | Multi-part integration result | Best from each prior part + composed result | Must cite component provenance |
| Frontier plot | Test metric vs total compute | Points per method/part | Pareto-optimal identification |

### 8.5 Unsupervised / RL Figures (Optional)

| Figure Type | When to Use | Content |
|------------|-------------|---------|
| Cluster visualization | 2D embedding of clusters | t-SNE/UMAP scatter colored by cluster label |
| Elbow / silhouette plot | Choosing cluster count | x=K, y=metric |
| Learning curve (RL) | Policy improvement over episodes | x=episodes, y=mean return ± std |
| Reward heatmap (RL) | State-value visualization | 2D state grid, color = value |

---

## 9) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Figure or table definitions (axes, series, required content, data sources)
- Summary table column list
- Filename conventions or directory layout
- Caption requirements
- Acceptance criteria
- Producer script identity
