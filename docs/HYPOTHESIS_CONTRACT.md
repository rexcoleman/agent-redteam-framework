# HYPOTHESIS CONTRACT

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §6 for EDA compatibility and prior-work continuity
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for metric definitions referenced in predictions

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §1 for experiment design grounded in hypotheses
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) §3 for hypothesis statements and §6 for resolution templates
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for Phase 2 hypothesis gate

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{DATASET_N_NAME}}` | Human-readable dataset name | Adult Income |
| `{{DATASET_N_EDA_OBSERVATION}}` | Key EDA finding driving the hypothesis | 3:1 class imbalance, high feature sparsity |
| `{{DATASET_N_PREDICTION}}` | Specific predicted outcome | Linear SVM will outperform DT on Adult |
| `{{DATASET_N_THEORY}}` | ML theory connecting EDA to prediction | Margin maximization is robust to sparse features |
| `{{DATASET_N_FAILURE_MODE}}` | Condition that would invalidate the prediction | High label noise causes SVM overfitting |
| `{{DATASET_N_METRIC}}` | Metric most relevant to this hypothesis | F1 (binary) |
| `{{DATASET_N_BASELINE_METRIC}}` | Baseline value for comparison | Accuracy = 0.758 (majority class) |
| `{{LOCK_COMMIT_SHA}}` | Git SHA of the commit that locks hypotheses | abc1234 |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines the hypothesis pre-registration protocol for the **Adversarial ML on Network Intrusion Detection** project. It ensures that testable predictions are formulated **before** experiments begin, grounded in EDA evidence and ML theory, preventing post-hoc rationalization.

**Core principle:** Hypotheses are predictions, not observations. They are written before results exist and resolved with quantitative evidence after experiments complete.

---

## 2) Temporal Gate

**Experiments MUST NOT begin before hypotheses are locked.**

The hypothesis lock is a hard phase gate:

1. Complete EDA for all datasets (see DATA_CONTRACT §6, IMPLEMENTATION_PLAYBOOK Phase 1)
2. Formulate hypotheses using the template in §4
3. Commit hypotheses with message: `HYPOTHESIS_LOCK: all hypotheses registered`
4. Record the lock commit SHA: `{{LOCK_COMMIT_SHA}}`
5. Only after this commit may experiment scripts be executed

**Enforcement:**
- Any experiment output with a git timestamp before the hypothesis lock commit is invalid
- Modifying a hypothesis after the lock requires a `CONTRACT_CHANGE` commit with justification
- Post-lock modifications MUST NOT change the predicted direction — only clarifications of scope or metric are permitted

---

## 3) Hypothesis Requirements

Every hypothesis MUST include all five components defined in §4. A hypothesis that omits any component is incomplete and MUST NOT be considered locked.

### Acceptance Checklist (per hypothesis)

- [ ] **Predicts a specific outcome** — not a vague expectation but a directional or quantitative claim
- [ ] **Grounded in EDA evidence** — cites a specific observation from EDA artifacts
- [ ] **Linked to ML theory** — names the mechanism connecting evidence to prediction
- [ ] **States a failure mode** — identifies what would cause the prediction to fail
- [ ] **Specifies a metric** — names the metric on which the prediction will be evaluated
- [ ] **Written before experiments** — committed before any experiment outputs exist

---

## 4) Per-Hypothesis Template

Copy this block for each hypothesis. Number sequentially: H-1, H-2, etc.

```markdown
### H-{{N}}: {{SHORT_TITLE}}

**Dataset:** {{DATASET_NAME}}

**Prediction:**
{{DATASET_N_PREDICTION}}

**EDA Evidence:**
{{DATASET_N_EDA_OBSERVATION}}
*(Cite specific artifact: e.g., "outputs/eda/adult_eda_summary.json shows 3:1 class imbalance")*

**Theory Link:**
{{DATASET_N_THEORY}}
*(Name the ML concept and explain the causal chain: EDA property → mechanism → predicted outcome)*

**Metric Focus:**
{{DATASET_N_METRIC}}
*(Why this metric is most relevant to testing this specific prediction)*

**Baseline Prediction:**
Relative to the baseline ({{DATASET_N_BASELINE_METRIC}}), I predict that [intervention]
will [improve / not improve] because [reasoning].

**Failure Mode:**
{{DATASET_N_FAILURE_MODE}}
*(What specific dataset property, hyperparameter setting, or assumption violation would cause
this prediction to fail?)*
```

---

## 5) Per-Dataset Hypothesis Example

<!-- Phase 2 trim candidate: §5 largely duplicates the §4 template with placeholders filled in.
     If this contract grows during Tier C deepening, consider replacing with a single condensed example. -->

### H-1: {{DATASET_1_NAME}} — {{DATASET_1_PREDICTION}}

**Dataset:** {{DATASET_1_NAME}}

**Prediction:**
{{DATASET_1_PREDICTION}}

**EDA Evidence:**
{{DATASET_1_EDA_OBSERVATION}}

**Theory Link:**
{{DATASET_1_THEORY}}

**Metric Focus:**
{{DATASET_1_METRIC}}

**Baseline Prediction:**
Relative to the baseline ({{DATASET_1_BASELINE_METRIC}}), I predict that [intervention] will [improve / not improve] because [reasoning].

**Failure Mode:**
{{DATASET_1_FAILURE_MODE}}

---

### H-2: {{DATASET_2_NAME}} — {{DATASET_2_PREDICTION}}

**Dataset:** {{DATASET_2_NAME}}

**Prediction:**
{{DATASET_2_PREDICTION}}

**EDA Evidence:**
{{DATASET_2_EDA_OBSERVATION}}

**Theory Link:**
{{DATASET_2_THEORY}}

**Metric Focus:**
{{DATASET_2_METRIC}}

**Baseline Prediction:**
Relative to the baseline ({{DATASET_2_BASELINE_METRIC}}), I predict that [intervention] will [improve / not improve] because [reasoning].

**Failure Mode:**
{{DATASET_2_FAILURE_MODE}}

*(Add additional hypotheses as needed. Multi-part projects may have hypotheses per experimental part.)*

---

## 6) Resolution Protocol

After experiments complete, every hypothesis MUST be formally resolved. Resolution is not optional — unresolved hypotheses are a delivery blocker.

### Resolution Template

Copy this block for each hypothesis resolution:

```markdown
### Resolution: H-{{N}}

**Verdict:** Confirmed | Refuted | Partially Confirmed

**Evidence:**
- Predicted: [restate the original prediction]
- Observed: [median = Y.YYY, IQR = [a, b], under Z budget, N seeds]
- Delta from baseline: [+/- X.XXX absolute change]

**Explanation:**
[Why the prediction was supported or contradicted. Cite the specific mechanism —
did the theory hold? Did the failure mode occur? What was unexpected?]

**Implications:**
[What this result means for the broader project or future work.]
```

---

## 7) Resolution Summary Table

Maintain this table as hypotheses are resolved. It provides a single-glance view of all predictions and outcomes.

| ID | Dataset | Prediction (short) | Metric | Predicted Direction | Observed Result | Verdict | Evidence Artifact |
|----|---------|-------------------|--------|--------------------|-----------------|---------|--------------------|
| H-1 | {{DATASET_1_NAME}} | *(summary)* | {{DATASET_1_METRIC}} | *(e.g., A > B)* | *(median ± IQR)* | *(Confirmed / Refuted / Partial)* | *(path to summary.json or figure)* |
| H-2 | {{DATASET_2_NAME}} | *(summary)* | {{DATASET_2_METRIC}} | *(e.g., A > B)* | *(median ± IQR)* | *(Confirmed / Refuted / Partial)* | *(path to summary.json or figure)* |
| *(add rows)* | | | | | | | |

### Verdict Criteria

| Verdict | Definition |
|---------|-----------|
| **Confirmed** | Observed result matches predicted direction AND magnitude is practically meaningful |
| **Refuted** | Observed result contradicts predicted direction OR effect is negligible |
| **Partially Confirmed** | Predicted direction holds for some conditions (e.g., one dataset but not another, or only under certain budgets) — requires explicit scope statement |

---

## 8) Traceability

### Hypotheses → Report Sections

Every hypothesis MUST appear in the report in two locations:

1. **Statement** (before results) — Section 3 or equivalent, using the hypothesis template language
2. **Resolution** (after results) — Discussion/Conclusion, with quantitative evidence and verdict

| Hypothesis | Stated In | Resolved In | Resolution Artifact |
|-----------|-----------|-------------|---------------------|
| H-1 | Report §3 | Report §Conclusion | `outputs/final_eval/...` |
| H-2 | Report §3 | Report §Conclusion | `outputs/final_eval/...` |
| *(add rows)* | | | |

### Hypotheses → Experiment Design

Each hypothesis SHOULD map to at least one experimental part or comparison. If a hypothesis cannot be tested by the planned experiments, either revise the hypothesis or add an experiment.

---

## 9) Acceptance Gate (Phase Exit Criteria)

Before proceeding to experiments, the following MUST pass:

- [ ] All hypotheses satisfy the acceptance checklist (§3)
- [ ] Hypotheses are committed with `HYPOTHESIS_LOCK` message
- [ ] Lock commit SHA recorded as `{{LOCK_COMMIT_SHA}}`
- [ ] No experiment outputs exist prior to the lock commit
- [ ] Each hypothesis maps to at least one planned experiment
- [ ] Resolution summary table (§7) is prepared with empty verdict/result columns

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Adding, removing, or modifying a hypothesis after lock
- Changing the predicted direction of any hypothesis
- Changing the metric focus of any hypothesis
- Modifying the resolution verdict after it has been recorded
- Changing the temporal gate rules
