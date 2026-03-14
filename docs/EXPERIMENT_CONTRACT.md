# EXPERIMENT CONTRACT

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §3 for split definitions and §4 for leakage prevention
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §8 for determinism and seeding defaults
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for required metrics and §5 for convergence threshold

**Downstream (depends on this contract):**
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §3 for experiment-sourced figures
- See [ARTIFACT_MANIFEST_SPEC](ARTIFACT_MANIFEST_SPEC.tmpl.md) §3 for per-run provenance files
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §4 for experiment script specifications

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{EXPERIMENT_PARTS}}` | List of experimental parts/phases | Part 1: RO, Part 2: Adam Ablations, Part 3: Regularization |
| `{{BUDGET_CONFIG_FILE}}` | Path to budget config | config/budgets.yaml |
| `{{BACKBONE_DESCRIPTION}}` | Model architecture description | PyTorch compact MLP from prior project |
| `{{SEED_LIST}}` | Stability seeds | [42, 123, 456, 789, 1024] |
| `{{DEFAULT_SEED}}` | Primary seed | 42 |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Scope & Experiment Matrix

This contract defines the experimental protocol for **Adversarial ML on Network Intrusion Detection**.

### 1.1 Experiment Parts

| Part | Description | Datasets | Methods | Budget Type |
|------|-------------|----------|---------|-------------|
| *(e.g.)* Part 1 | *(e.g.)* Randomized Optimization | *(e.g.)* Adult + Wine | *(e.g.)* RHC, SA, GA | func_evals |
| *(e.g.)* Part 2 | *(e.g.)* Optimizer Ablations | *(e.g.)* Adult only | *(e.g.)* 7 optimizers | grad_evals |
| *(e.g.)* Part 3 | *(e.g.)* Regularization Study | *(e.g.)* Adult only | *(e.g.)* 4 techniques + combo | grad_evals |
| *(add parts)* | | | | |

### 1.2 Cross-Part Constraints

Document hard rules that constrain relationships between parts:

| Constraint | Rule | Enforcement |
|-----------|------|-------------|
| *(e.g.)* Dataset lock | Parts 2-3 run on {{DATASET_NAME}} only | Script validates `--dataset` flag |
| *(e.g.)* Architecture lock | Backbone unchanged across parts | Config diff assertion at phase gate |
| *(e.g.)* HP inheritance | Part 3 uses locked best HPs from Part 2 | Config loaded from Part 2 best run |
| *(add rows)* | | |

### 1.3 Cross-Part Dependency Graph

```
Part 1 ──→ Part 4 (best RO algorithm)
Part 2 ──→ Part 3 (locked optimizer HPs)
Part 2 ──→ Part 4 (locked optimizer HPs)
Part 3 ──→ Part 4 (best regularization combo)
```

*(Adapt this graph to your project's part dependencies. An arrow means "results from the source part feed into the target part.")*

---

## 2) Compute Budgets

### 2.1 Budget Source

All budgets are defined in `{{BUDGET_CONFIG_FILE}}`. Scripts read values at runtime. No hardcoded budgets in code.

### 2.2 Budget Types

Different experiment paradigms use different budget accounting:

| Budget Type | Unit | When to Use | Counting Rule |
|------------|------|-------------|---------------|
| `func_evals` | Function evaluations | Black-box optimization, randomized search, evolutionary methods | Each objective function computation (including full validation sweep) counts as ONE evaluation |
| `grad_evals` | Gradient evaluations | Gradient-based training (SGD, Adam, etc.) | Each backward pass counts as ONE gradient evaluation; multiple batches per step still count as one |
| `episodes` | Environment episodes | RL / sequential decision-making | Each complete episode (reset → terminal) counts as ONE episode |
| `wall_clock` | Seconds | Real-time constrained experiments | Cumulative wall-clock time; MUST be reported alongside primary budget |

**Accounting rules:**
- Every run MUST log both `budget_allocated` and `budget_used` in `summary.json`
- If validation is computed via mini-batches for memory efficiency, the entire sweep still counts as ONE function evaluation
- Wall-clock MUST be reported alongside the primary budget type for all experiments (even if wall-clock is not the budget constraint)

**Verification:** Schema-validate every `summary.json` for presence of `budget_allocated`, `budget_used`, and `wall_clock_s` fields.

### 2.3 Budget Schema

```yaml
# {{BUDGET_CONFIG_FILE}}
part1:
  func_evals: {{PART1_BUDGET}}
part2:
  grad_evals: {{PART2_BUDGET}}
  eval_interval_steps: {{EVAL_INTERVAL}}
  threshold_l: {{THRESHOLD_L}}
part3:
  grad_evals: {{PART3_BUDGET}}  # MUST equal part2.grad_evals
seeds:
  default: {{DEFAULT_SEED}}
  stability_list: {{SEED_LIST}}
```

### 2.4 Budget-Matching Rule

Within each part, all compared methods MUST use identical compute budgets. This is non-negotiable for fair comparisons.

- Scripts MUST enforce budget caps and hard-stop at the limit (no silent overruns)
- Over-budget runs MUST set `over_budget: true` in `summary.json`
- Over-budget runs MUST be excluded from head-to-head comparison tables and claims
- Over-budget runs MAY be reported in supplementary analysis with clear disclosure

**Verification:** At each phase gate, assert that all runs within a part have `budget_used <= budget_allocated` and that `budget_allocated` is identical across methods.

### 2.5 Cross-Part Budget Consistency

Where experiments in different parts are compared (e.g., regularization vs baseline), budgets MUST match. Specifically:
- `part3.grad_evals == part2.grad_evals` (if Part 3 builds on Part 2)
- This is validated at Phase 0 and enforced in scripts

---

## 3) Dataset Splits & Leakage Prevention

### 3.1 Split Source

*(Reference DATA_CONTRACT for full details.)*

Split files: `data/splits/{{DATASET_NAME}}/split_seed{{SEED}}.json`

### 3.2 Test-Split Access Policy

Test split is accessible ONLY through the final evaluation script. All other scripts MUST use train and validation splits only.

### 3.3 Leakage Prevention

- Fit preprocessing on train only (see DATA_CONTRACT §4)
- No test metrics in per-run outputs
- No hyperparameter selection based on test performance

---

## 4) Seeding & Initialization Protocol

### 4.1 Seed Policy

- **Default seed:** {{DEFAULT_SEED}}
- **Stability list:** {{SEED_LIST}}
- Seeds are set before every experiment via the deterministic seeding function (see ENVIRONMENT_CONTRACT §8)

### 4.2 Baseline State Matching

For experiments that compare different methods on the same system, all methods MUST start from an identical baseline state. The exact form of the baseline depends on the project domain:

| Domain | Baseline State | Verification Method |
|--------|---------------|-------------------|
| **Neural networks** | Initial weight `state_dict` | Forward-pass equality within tolerance (1e-6) |
| **Systems / C/C++** | Compiled binary + input data + initial memory state | Binary hash equality + input hash equality |
| **RL agents** | Initial policy weights + environment seed | First-episode trajectory equality |

**Verification:** All methods within a part share an identical baseline. The verification method above confirms equality at run start.

#### Protocol (Neural Network Projects)

1. **Initialize once per seed:** Create the model with the current seed and save the initial `state_dict`:
   ```python
   torch.manual_seed(seed)
   model = build_model(config)
   torch.save(model.state_dict(), f"outputs/init_weights/{{DATASET}}_seed_{seed}.pt")
   ```

2. **Load before each run:** Before each method's training begins, load the saved `state_dict`:
   ```python
   model.load_state_dict(torch.load(f"outputs/init_weights/{{DATASET}}_seed_{seed}.pt"))
   ```

3. **Verify identical start:** Assert that all methods produce the same first-batch forward-pass output:
   ```python
   # After loading init weights, before training:
   with torch.no_grad():
       output = model(X_sample)
   # Compare against reference output from first method — must match within tolerance
   assert torch.allclose(output, reference_output, atol=1e-6), \
       f"Init mismatch: method {method} diverges from reference at seed {seed}"
   ```

#### Protocol (Systems / C/C++ Projects)

1. **Build once per configuration:** Compile the binary with locked build profile (see BUILD_SYSTEM_CONTRACT §3). Record binary hash.
2. **Share input data:** All compared methods receive identical input files. Record input hashes.
3. **Verify identical start:** Assert binary hash and input hash match across all method runs.

#### Storage Convention

```
outputs/init_weights/          # Neural network projects
├── {{DATASET_1_NAME}}_seed_42.pt
├── {{DATASET_1_NAME}}_seed_123.pt
└── ...

outputs/baseline_state/        # Systems projects
├── binary_hash.json
├── input_hashes.json
└── ...
```

#### Scope

Baseline state matching applies to:
- All methods within a single part (e.g., all optimizers in Part 2)
- All methods across dependent parts (e.g., Part 3 uses the same init as Part 2)
- Part composition experiments (e.g., Part 4 gradient phase uses the same init)

Baseline state matching does NOT apply to:
- Methods with fundamentally different architectures (if permitted by the experiment design)
- Black-box optimization phases where the "initialization" is the pre-trained weights from a prior phase

### 4.3 Multi-Seed Stability

All experiments MUST be run across the full seed list to support:
- Median + IQR reporting (not just single-seed point estimates)
- Stability analysis across methods
- Credible dispersion in comparative claims

**Verification:** For each method, assert that `len(completed_seeds) == len(stability_list)`. Multi-seed outputs exist under `outputs/{{PART}}/{{DATASET}}/{{METHOD}}/seed_*/`.

---

## 5) Metrics & Evaluation Rules

*(Reference METRICS_CONTRACT for full definitions.)*

### 5.1 Evaluation Determinism

During evaluation (validation loss computation, metric calculation):
- `model.eval()` MUST be called
- Dropout MUST be disabled
- Batch normalization MUST be frozen (running stats, not batch stats)
- Data augmentation MUST be disabled
- `torch.no_grad()` MUST wrap the evaluation block

**Verification:** Assert `model.training == False` during evaluation. Verify `config_resolved.yaml` records `eval_mode: True`, `dropout_off: True`, `bn_frozen: True`.

### 5.2 Required Metrics Per Run

Every run MUST log:
- `train_loss` and `val_loss` at every evaluation interval
- Primary validation metric(s) per dataset
- `wall_clock_s` cumulative timing
- Budget usage (`grad_evals` or `func_evals`)

---

## 6-N) Per-Part Protocols

*(Create one section per experimental part. Each section should define:)*

### Part {{N}}: {{PART_NAME}}

**Goal:** *(One-sentence description)*

**Methods:** *(List all methods/algorithms to be compared)*

**Budget:** `{{BUDGET_CONFIG_KEY}}` from `{{BUDGET_CONFIG_FILE}}`

**Protocol:**
1. *(Step-by-step procedure)*
2. *(What to initialize, what to vary, what to hold constant)*
3. *(What to log beyond standard metrics)*

**Operator Disclosures:** *(For each method, list what hyperparameters/settings must be reported)*

| Method | Required Disclosures |
|--------|---------------------|
| *(e.g.)* RHC | Restart policy, step-size schedule |
| *(e.g.)* SA | Initial temperature, decay factor, cooling schedule |
| *(e.g.)* GA | Population size, selection, crossover, mutation rate, elitism |

**Constraints:**
- *(e.g.)* All methods must start from the same init weights
- *(e.g.)* Architecture must not be modified (except for Part 3 regularization modules)
- *(e.g.)* Locked hyperparameters from prior parts must not be retuned

---

## {{N+1}}) Output Directory Structure

```
outputs/
+-- init_weights/                          # Saved initial state_dicts
+-- part1/{{DATASET}}/{{METHOD}}/seed_*/   # Part 1 outputs
+-- part2/{{DATASET}}/{{METHOD}}/seed_*/   # Part 2 outputs
+-- part3/{{DATASET}}/{{METHOD}}/seed_*/   # Part 3 outputs
+-- sanity_checks/                         # Sanity check results
+-- final_eval/seed_*/                     # Final test evaluation
+-- figures/                               # Generated figures
+-- tables/                                # Generated tables
```

### Per-Run Output Files

Every run directory MUST contain:

| File | Format | Contents |
|------|--------|----------|
| `metrics.csv` | CSV | Per-step metrics (see METRICS_CONTRACT §9) |
| `summary.json` | JSON | Run summary with best metrics, budget usage, flags |
| `config_resolved.yaml` | YAML | Full resolved configuration (CLI + config file + defaults) |
| `run_manifest.json` | JSON | SHA-256 hashes of all output files |

**Verification:** `python scripts/verify_manifests.py` checks that all four files exist in every run directory and that `run_manifest.json` hashes are correct.

---

## {{N+2}}) Pipeline Composition Protocol

When an experiment part composes results from prior parts (e.g., "use best optimizer from Part 2 + best regularization from Part 3 + best RO algorithm from Part 1"), the following rules apply.

### Composition Invariants

1. **Locked selections:** Each component MUST use the exact configuration from the prior part's best run. No retuning of previously locked hyperparameters.
2. **Configuration trace:** The composed run's `config_resolved.yaml` MUST include provenance for each component:

```yaml
composition:
  optimizer:
    source_part: 2
    source_run_id: "part2_adam_seed42"
    locked_params: {lr: 0.001, beta1: 0.9, beta2: 0.999}
  regularization:
    source_part: 3
    source_run_id: "part3_best_combo_seed42"
    locked_params: {dropout: 0.3, l2_lambda: 0.001}
  fine_tuning:
    source_part: 1
    source_method: "sa"
    locked_params: {init_temp: 1.0, decay: 0.99}
```

3. **Budget constraints:** Composition parts may have separate budgets for each phase (e.g., gradient training budget + RO fine-tuning budget). Each phase's budget MUST be declared separately.
4. **Seed consistency:** Seeds, hardware class, data splits, and batch size MUST match earlier parts.

### Composition Exit Gate Additions

- [ ] Each component traces to a specific prior part run ID
- [ ] No hyperparameter was retuned from its locked value
- [ ] Phase-specific budgets are within limits
- [ ] Results are comparable to prior parts (same metrics, same evaluation protocol)

---

## {{N+3}}) Exit Gates

Each experimental part has an exit gate that MUST pass before proceeding.

### Exit Gate Template

- [ ] All methods complete for all seeds
- [ ] Budget usage is consistent across methods (within tolerance)
- [ ] No over-budget runs (or properly flagged and excluded)
- [ ] Required metrics logged in every `summary.json`
- [ ] `metrics.csv` has expected columns and row counts
- [ ] Operator disclosures present in `config_resolved.yaml`
- [ ] Init-weight verification passed (forward-pass match within tolerance)
- [ ] *(Part-specific checks)*

---

## {{N+4}}) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Compute budgets (any value in `{{BUDGET_CONFIG_FILE}}`)
- Method list for any part
- Initialization protocol
- Output schemas (metrics.csv, summary.json, config_resolved.yaml)
- Evaluation determinism rules
- Budget-matching constraints
- Part composition rules
- Cross-part constraints or dependency graph

---

## Appendix A: Sequential / RL Experiment Protocol (Optional)

> **Activation:** Include this appendix when your project involves reinforcement learning, sequential
> decision-making, or episode-based experiments. Delete if not applicable.

### A.1 Episode-Based Budget Accounting

| Budget Type | Unit | Counting Rule |
|------------|------|---------------|
| `episodes` | Complete episodes | Each reset → terminal transition counts as ONE episode |
| `env_steps` | Environment steps | Each `env.step()` call counts as ONE step |
| `wall_clock` | Seconds | Cumulative wall-clock (always reported alongside primary budget) |

### A.2 Environment Specification

The environment MUST be fully specified in a companion [ENVIRONMENT_SPEC](ENVIRONMENT_SPEC.tmpl.md) document (if available) or in this section:

| Property | Value |
|----------|-------|
| **Environment** | adversarial-ids |
| **State space** | {{STATE_SPACE_DESCRIPTION}} |
| **Action space** | {{ACTION_SPACE_DESCRIPTION}} |
| **Reward function** | {{REWARD_DESCRIPTION}} |
| **Episode termination** | {{TERMINATION_CONDITION}} |
| **Max episode length** | {{MAX_EPISODE_STEPS}} |

### A.3 Policy Evaluation Protocol

- **Evaluation frequency:** Every {{EVAL_INTERVAL_EPISODES}} training episodes
- **Evaluation method:** {{EVAL_EPISODES}} episodes with greedy/deterministic policy (no exploration noise)
- **Metrics logged per evaluation:** mean return, std return, mean episode length, success rate (if applicable)

### A.4 Reproducibility Requirements

- Environment seed MUST be set via `env.reset(seed=seed)` at the start of each episode
- For stochastic environments, evaluation MUST use a fixed set of seeds separate from training seeds
- Random exploration noise MUST be seeded deterministically

### A.5 RL-Specific Logging

Every run's `metrics.csv` MUST include:

```
episode,env_steps,train_return,eval_mean_return,eval_std_return,eval_mean_length,wall_clock_sec
```

Every run's `summary.json` MUST include:
```json
{
  "budget_allocated": {"episodes": null, "env_steps": null},
  "budget_used": {"episodes": null, "env_steps": null},
  "best_eval_return": null,
  "best_eval_episode": null,
  "total_env_steps": null
}
```
