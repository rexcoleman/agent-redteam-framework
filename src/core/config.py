"""Configuration loader with layered override support.

Reads base.yaml then merges agent/attack/defense overrides per CONFIGURATION_SPEC.
"""

import yaml
from pathlib import Path
from typing import Any


def load_config(
    base_path: str = "config/base.yaml",
    overrides: list[str] | None = None,
) -> dict[str, Any]:
    """Load base config and merge overrides (last wins)."""
    base = Path(base_path)
    if not base.exists():
        raise FileNotFoundError(f"Base config not found: {base}")

    with open(base) as f:
        config = yaml.safe_load(f)

    for override_path in overrides or []:
        p = Path(override_path)
        if p.exists():
            with open(p) as f:
                override = yaml.safe_load(f) or {}
            config = _deep_merge(config, override)

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Override wins on conflicts."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_llm_config(config: dict) -> dict:
    """Extract LLM provider config."""
    return config.get("llm", {})


def get_agent_config(config: dict, agent_name: str) -> dict:
    """Extract config for a specific agent target."""
    agents = config.get("agents", {})
    if agent_name not in agents:
        raise ValueError(f"Unknown agent: {agent_name}. Available: {list(agents.keys())}")
    return agents[agent_name]


def get_attack_config(config: dict, attack_name: str) -> dict:
    """Extract config for a specific attack class."""
    attacks = config.get("attacks", {})
    if attack_name not in attacks:
        raise ValueError(f"Unknown attack: {attack_name}. Available: {list(attacks.keys())}")
    return attacks[attack_name]
