# ENVIRONMENT CONTRACT

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
- None — this is a foundational contract.

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §4 for seeding and initialization protocol
- See [PRIOR_WORK_REUSE](../management/PRIOR_WORK_REUSE.tmpl.md) §3 for environment compatibility assessment
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §3 for environment verification scripts (`verify_env.sh`)
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for Phase 0 environment lock gate

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `3.11` | Pinned Python version | 3.10.13 |
| `conda` | Environment manager | mamba / conda / pip+venv |
| `adversarial-ids` | Environment name | my-ml-project |
| `environment.yml` | Environment definition file | environment.yml / requirements.txt |
| `{{PLATFORM}}` | Target platform | Linux CPU-only |
| `docs/PROJECT_BRIEF.md` | Tier 1 authority document | Project requirements spec |
| `null # No external FAQ` | Tier 2 authority document | FAQ or clarifications document |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 3 authority document | Course TAs' Piazza clarifications |
| `{{REPRO_COMMANDS}}` | Exact reproduction command sequence | See §7 |

---

## 1) Purpose

This contract locks the compute environment for the **Adversarial ML on Network Intrusion Detection** project. It ensures that all artifacts are reproducible on the target platform by any reviewer.

---

## 2) Target Platform

- **OS:** {{PLATFORM}}
- **Hardware:** *(e.g., CPU-only, GPU optional for exploration)*
- **Constraint:** All final deliverables MUST be reproducible on the target platform. GPU may be used for exploration but MUST NOT be required for release artifacts.

**Verification:** `bash scripts/verify_env.sh` exits 0 on target platform. Re-run a representative experiment on CPU and compare output hashes.

---

## 3) Locked Language & Runtime

- **Language:** Python 3.11
- **Package manager:** conda
- **Environment name:** adversarial-ids

---

## 4) Dependencies

All dependencies are locked in `environment.yml`. Key packages:

| Package | Version | Purpose |
|---------|---------|---------|
| *(e.g.)* numpy | 1.26.4 | Numerical computation |
| *(e.g.)* pandas | 2.1.4 | Data manipulation |
| *(e.g.)* scikit-learn | 1.7.2 | ML utilities |
| *(e.g.)* pytorch | 2.2.2 | Neural network framework |
| *(e.g.)* matplotlib | 3.8.2 | Plotting |

*(Fill in actual pinned versions from your environment file.)*

---

## 5) Environment Setup

```bash
# Create environment
conda env create -f environment.yml
conda activate adversarial-ids

# Verify environment
bash scripts/verify_env.sh
```

The verification script MUST:
- Print Python version and confirm it matches 3.11
- Print versions of all key packages
- Confirm target platform compatibility (e.g., `cuda_available: False` is acceptable for CPU-only)
- Exit 0 on success, 1 on any mismatch

---

## 6) Data Placement

*(Reference DATA_CONTRACT for canonical paths. Provide copy-paste instructions for the REPRO document.)*

```
data/raw/{{DATASET_1_FILE}}  — {{DATASET_1_DESCRIPTION}}
data/raw/{{DATASET_2_FILE}}  — {{DATASET_2_DESCRIPTION}}
```

Data source: {{DATA_SOURCE}} *(e.g., "download from Kaggle", "download from UCI ML Repository")*

---

## 7) Reproduction Commands

All commands run from repository root. These are the canonical commands that appear in the REPRO document.

```bash
# Phase 0: Environment
conda env create -f environment.yml
conda activate adversarial-ids
bash scripts/verify_env.sh

# Phase 1: Data verification & EDA
# (Fill in project-specific commands)

# Phase 2-N: Experiments
# (Fill in project-specific commands)

# Final: Evaluation & artifact generation
# (Fill in project-specific commands)
```

---

## 8) Determinism Defaults

The following determinism settings MUST be applied in all experiment scripts.

**Verification:** Grep all experiment scripts for `set_seed` or equivalent call. Run same experiment twice with same seed; compare output hashes for byte-identical results.

```python
import random
import numpy as np
import torch

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
```

- **Default seed:** {{DEFAULT_SEED}} *(e.g., 42)*
- **Stability seed list:** {{SEED_LIST}} *(e.g., [42, 123, 456, 789, 1024])*
- **n_jobs:** Always 1 (no parallel workers) unless explicitly justified and documented

---

## 9) Provenance Outputs

The first experiment run MUST produce:

| File | Path | Contents |
|------|------|----------|
| `versions.txt` | `outputs/provenance/versions.txt` | Package versions at runtime |
| `git_commit_sha.txt` | `outputs/provenance/git_commit_sha.txt` | Current git SHA |
| `run_log.json` | `outputs/provenance/run_log.json` | Append-only log of all runs |

---

## 10) CPU Reproducibility Rule

ALL report artifacts MUST be reproducible on CPU. This is non-negotiable for independent verification.

- Environment file MUST include a CPU-only build of the ML framework
- Scripts MUST NOT fail if GPU is unavailable
- Final artifacts MUST be generated on CPU

**Verification:** `bash scripts/verify_env.sh` logs `cuda_available` status. All scripts exit 0 when `torch.cuda.is_available() == False`.

---

## 11) Change Control

The following changes require a `CONTRACT_CHANGE` commit:

- Python version (including patch)
- Any dependency in `environment.yml` (add, remove, or version change)
- Determinism or leakage guardrails
- Seed policy
- `n_jobs` settings
- Script filenames, CLI parameters, or entrypoint paths
- Data paths
- Budget values

---

## Appendix D: C/C++ Determinism Defaults (Optional)

> **Activation:** Include this appendix when your project uses compiled languages (C, C++, Rust).
> Delete if not applicable. When activated, §8 Determinism Defaults should be replaced or
> supplemented with these C/C++ equivalents.

### D.1 PRNG Seeding

```cpp
#include <random>
#include <cstdlib>

void set_seed(unsigned seed) {
    // C++ Mersenne Twister — deterministic across platforms with same seed
    std::mt19937 rng(seed);

    // C stdlib (if used)
    srand(seed);
}
```

**Rule:** All randomness MUST flow through `std::mt19937` (or `std::mt19937_64`) seeded from the command-line seed argument. `rand()` is acceptable only in legacy code with documented justification.

### D.2 Thread Pool Determinism

For multithreaded experiments:

| Requirement | Rule |
|-------------|------|
| **Thread pool size** | Fixed at runtime, specified via CLI flag (`--threads N`) |
| **Work distribution** | Deterministic assignment (round-robin or static partitioning, NOT work-stealing) |
| **Reduction order** | Fixed reduction order for floating-point accumulation (e.g., always left-to-right) |

**Rule:** Thread pool size MUST be locked per experiment configuration. Dynamic thread pools (e.g., OpenMP `schedule(dynamic)`) are PROHIBITED for reproducibility-critical paths unless results are order-independent.

**Verification:** `config_resolved.yaml` records `thread_count`. Same experiment with same thread count and seed produces identical output.

### D.3 Compiler Optimization Governance

| Optimization Level | Determinism Impact | Rule |
|-------------------|-------------------|------|
| `-O0` | Deterministic | Debug profile only |
| `-O1` | Deterministic | Acceptable |
| `-O2` | Generally deterministic | Default for benchmarks |
| `-O3` | May reorder operations | MUST verify determinism if used |
| `-Ofast` / `-ffast-math` | Non-deterministic FP | PROHIBITED for reproducibility-critical code |

**Rule:** `-ffast-math` and `-Ofast` are PROHIBITED in any build profile where numeric reproducibility is required. See [BUILD_SYSTEM_CONTRACT](BUILD_SYSTEM_CONTRACT.tmpl.md) §3 for locked profiles.

### D.4 ASLR Control

Address Space Layout Randomization can affect pointer-dependent hash maps and certain allocator behaviors:

```bash
# Disable ASLR for the benchmark process
setarch $(uname -m) -R ./benchmark --seed {{DEFAULT_SEED}}
```

**Rule:** ASLR MUST be disabled for all benchmark runs. ASLR state MUST be logged in `benchmark_env.json`.

### D.5 Floating-Point Determinism

| Requirement | Rule |
|-------------|------|
| **FP contraction** | `-ffp-contract=off` to prevent FMA fusion variance |
| **FP rounding** | Default rounding mode (`FE_TONEAREST`) — do not modify |
| **Cross-platform** | Do NOT assume bitwise FP equality across compilers; use tolerance-based comparison |
