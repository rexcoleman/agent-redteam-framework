#!/usr/bin/env bash
# reproduce.sh — Reproduce FP-02 Agent Red-Team Framework results.
#
# This project requires an Anthropic API key (Claude Sonnet) for full
# attack/defense execution. Without it, you can still run the test suite
# and regenerate figures from existing JSON data.
#
# Usage:
#   ./reproduce.sh              # Run tests + figures (no API key needed)
#   ANTHROPIC_API_KEY=sk-... ./reproduce.sh   # Full reproduction
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== Agent Red-Team Framework — Reproduction Script ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Root: $ROOT"
echo ""

# ---------------------------------------------------------------
# Step 1: Check / create conda environment
# ---------------------------------------------------------------
echo "--- Step 1: Environment setup ---"
if command -v conda &>/dev/null; then
    if conda env list | grep -q "agent-redteam"; then
        echo "Conda env 'agent-redteam' already exists. Activating..."
        eval "$(conda shell.bash hook 2>/dev/null)"
        conda activate agent-redteam
    else
        echo "Creating conda env from environment.yml..."
        conda env create -f environment.yml
        eval "$(conda shell.bash hook 2>/dev/null)"
        conda activate agent-redteam
    fi
else
    echo "WARNING: conda not found. Assuming dependencies are installed in current Python."
    echo "  Install with: pip install pytest pyyaml matplotlib numpy"
fi
echo ""

# ---------------------------------------------------------------
# Step 2: Run test suite (no API key required)
# ---------------------------------------------------------------
echo "--- Step 2: Running test suite ---"
python -m pytest tests/ -v --tb=short
echo ""

# ---------------------------------------------------------------
# Step 3: Check for API key
# ---------------------------------------------------------------
HAS_API_KEY=false
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "--- Step 3: ANTHROPIC_API_KEY detected ---"
    HAS_API_KEY=true
else
    echo "--- Step 3: No ANTHROPIC_API_KEY found ---"
    echo "  Skipping live scenario execution."
    echo "  Set ANTHROPIC_API_KEY to run full attack/defense scenarios."
fi
echo ""

# ---------------------------------------------------------------
# Step 4: Run scenarios (dry-run if no API key, live if key present)
# ---------------------------------------------------------------
if [[ "$HAS_API_KEY" == "true" ]]; then
    echo "--- Step 4: Running attack scenarios (live) ---"
    for seed in 42 123 456; do
        echo "  Seed $seed: LangChain ReAct, all attack classes..."
        python scripts/run_attacks.py \
            --agent langchain_react \
            --attack all \
            --seed "$seed"
    done

    echo "  Seed 42: CrewAI multi-agent, prompt injection..."
    python scripts/run_attacks.py \
        --agent crewai_multi \
        --attack prompt_injection \
        --seed 42

    echo ""
    echo "--- Step 4b: Running defense scenarios ---"
    for defense in input_sanitizer layered full; do
        echo "  Defense: $defense (seed 42)..."
        python scripts/run_defenses.py \
            --agent langchain_react \
            --defense "$defense" \
            --seed 42
    done
else
    echo "--- Step 4: Dry-run mode (no API key) ---"
    echo "  Verifying scenario configurations parse correctly..."
    python scripts/run_attacks.py --dry-run 2>/dev/null || \
        echo "  (dry-run flag not implemented — skipping)"
fi
echo ""

# ---------------------------------------------------------------
# Step 5: Generate figures from JSON data
# ---------------------------------------------------------------
echo "--- Step 5: Generating figures from existing JSON data ---"
if [[ -d outputs/attacks ]] && [[ -n "$(ls outputs/attacks/)" ]]; then
    python scripts/generate_figures.py --output-dir outputs/figures --data-dir outputs
    echo ""
    echo "Figures written to outputs/figures/:"
    ls -lh outputs/figures/*.png 2>/dev/null || echo "  (no figures generated)"
else
    echo "  No attack output data found in outputs/attacks/."
    echo "  Run with ANTHROPIC_API_KEY to generate data first."
fi
echo ""

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
echo "=== Reproduction complete ==="
echo ""
echo "Artifacts:"
echo "  Tests:    pytest results above"
echo "  Figures:  outputs/figures/*.png"
echo "  Data:     outputs/attacks/*/summary.json"
echo "             outputs/defenses/*/summary.json"
echo ""
if [[ "$HAS_API_KEY" == "true" ]]; then
    echo "Full reproduction completed with live API calls."
else
    echo "Partial reproduction (tests + figures only)."
    echo "Set ANTHROPIC_API_KEY for full reproduction with live API calls."
fi

# --- Gate Validation (R50) ---
if [ -f "$HOME/ml-governance-templates/scripts/check_all_gates.sh" ]; then
    echo "--- Gate Validation (R50) ---"
    bash "$HOME/ml-governance-templates/scripts/check_all_gates.sh" .
else
    echo "WARN: govML not found — skipping gate validation (R50)"
fi
