> **⚠️ ARCHIVED** — This project is archived. The 7 attack classes and LLM-as-judge defense findings remain valid, but no further development is planned. Agent security research continues in [multi-agent-security](https://github.com/rexcoleman/multi-agent-security) and [agent-semantic-resistance](https://github.com/rexcoleman/agent-semantic-resistance).

# Agent Security Red-Team Framework

Reasoning chain hijacking hits 100% success against default LangChain ReAct agents. 7 attack classes systematized — 5 absent from OWASP LLM Top 10 and MITRE ATLAS. Layered defense reduces overall success by 60%.

**Blog post:** [I Red-Teamed AI Agents: Here's How They Break](https://rexcoleman.dev/posts/agent-redteam/)

## Key Findings

- **7 attack classes** systematized into a reusable taxonomy (5 not covered by OWASP LLM Top 10 / MITRE ATLAS)
- **Reasoning chain hijacking**: 100% success rate against default-configured LangChain ReAct agents (Claude Sonnet, 3 seeds) — the most dangerous agent-specific attack pattern tested
- **Layered defense** reduces overall attack success by 60%
- **Adversarial control analysis** validated across 3 domains (IDS, CVE prediction, agents)

![Attack Success Rates](blog/images/attack_success_rates.png)

![Defense Comparison](blog/images/defense_comparison.png)

## Quick Start

```bash
# Clone and install
git clone https://github.com/rexcoleman/agent-redteam-framework.git
cd agent-redteam-framework
conda env create -f environment.yml
conda activate agent-redteam
pip install -e .

# Set your API key
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Verify environment
agent-redteam verify-env

# Run attacks against LangChain ReAct agent
agent-redteam scan --agent langchain_react --attack all --seed 42

# Evaluate defenses
agent-redteam defend --agent langchain_react --defense layered --seed 42

# Generate figures
agent-redteam figures
```

## Attack Taxonomy

| Class | Success Rate | Status |
|-------|-------------|--------|
| Direct Prompt Injection | 80% | Known (OWASP LLM01) |
| Indirect Injection via Tools | 25% | Partially known |
| **Tool Permission Boundary Violation** | **75%** | **Systematized** |
| **Memory/Context Poisoning** | **67%** | **Systematized** |
| **Reasoning Chain Hijacking** | **100%** | **Novel pattern** |

See [`docs/attack_taxonomy.md`](docs/attack_taxonomy.md) for the full taxonomy and [`FINDINGS.md`](FINDINGS.md) for detailed results.

## Architecture

```
src/
  agents/           # Agent target abstractions (LangChain, CrewAI)
  attacks/          # Attack class implementations
  defenses/         # Defense layers (input sanitizer, tool boundary, layered)
  core/             # Config, types, logging
  cli.py            # CLI entry point
scripts/            # Experiment runners + govML-generated scripts
config/             # YAML configuration (agents, attacks, defenses)
data/tasks/         # YAML-driven attack scenarios
docs/               # govML governance documents (22 templates)
blog/               # Blog draft + conference abstract + images
```

## Project Governance

Built with [govML](https://github.com/rexcoleman/govML) v2.4 (security-ml profile, 22 templates). Key governance documents:

- [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) — Thesis, research questions, success criteria
- [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md) — 3 architecture decision records
- [`docs/ADVERSARIAL_EVALUATION.md`](docs/ADVERSARIAL_EVALUATION.md) — Threat model + controllability matrix
- [`docs/PUBLICATION_PIPELINE.md`](docs/PUBLICATION_PIPELINE.md) — Blog distribution governance

## License

MIT
