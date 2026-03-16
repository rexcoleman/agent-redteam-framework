"""Tests for attack scenario YAML integrity.

Validates that all scenario files parse correctly, contain required fields,
use valid attack class names, have unique IDs, and match documentation counts.

NO API calls. All tests operate on static YAML files.
"""
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
SCENARIO_PATH = ROOT / "data" / "tasks" / "attack_scenarios.yaml"

# Known attack classes from docs/attack_taxonomy.md (implemented in scenarios)
IMPLEMENTED_CLASSES = {
    "prompt_injection",
    "indirect_injection",
    "tool_boundary",
    "memory_poisoning",
    "reasoning_hijack",
}

# Full taxonomy includes 7 classes; 2 are defined but not yet scenario-implemented
FULL_TAXONOMY_CLASSES = IMPLEMENTED_CLASSES | {
    "cross_agent_escalation",
    "output_format_exploitation",
}


@pytest.fixture
def attack_scenarios():
    """Load and return the attack scenarios dict."""
    with open(SCENARIO_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture
def all_scenarios_flat(attack_scenarios):
    """Flatten all scenarios into a list of (class_name, scenario) tuples."""
    flat = []
    for cls, scenarios in attack_scenarios["attacks"].items():
        for s in scenarios:
            flat.append((cls, s))
    return flat


class TestScenarioParsing:

    def test_yaml_parses_without_error(self):
        """attack_scenarios.yaml parses as valid YAML."""
        with open(SCENARIO_PATH) as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert isinstance(data, dict)

    def test_top_level_key_is_attacks(self, attack_scenarios):
        """Top-level key 'attacks' exists and is a dict."""
        assert "attacks" in attack_scenarios
        assert isinstance(attack_scenarios["attacks"], dict)

    def test_each_class_has_at_least_one_scenario(self, attack_scenarios):
        """Every attack class in the file has at least one scenario."""
        for cls, scenarios in attack_scenarios["attacks"].items():
            assert len(scenarios) >= 1, f"Class '{cls}' has zero scenarios"


class TestScenarioRequiredFields:

    def test_all_scenarios_have_id(self, all_scenarios_flat):
        """Every scenario has an 'id' field."""
        for cls, s in all_scenarios_flat:
            assert "id" in s, f"Scenario in class '{cls}' missing 'id'"

    def test_all_scenarios_have_prompt(self, all_scenarios_flat):
        """Every scenario has a 'prompt' field (the attack payload)."""
        for cls, s in all_scenarios_flat:
            assert "prompt" in s, (
                f"Scenario {s.get('id', '?')} in class '{cls}' missing 'prompt'"
            )

    def test_all_scenarios_have_goal(self, all_scenarios_flat):
        """Every scenario has a 'goal' field describing expected outcome."""
        for cls, s in all_scenarios_flat:
            assert "goal" in s, (
                f"Scenario {s.get('id', '?')} in class '{cls}' missing 'goal'"
            )

    def test_prompts_are_nonempty_strings(self, all_scenarios_flat):
        """All prompt fields are non-empty strings."""
        for cls, s in all_scenarios_flat:
            prompt = s.get("prompt", "")
            assert isinstance(prompt, str) and len(prompt) > 0, (
                f"Scenario {s['id']} has empty or non-string prompt"
            )


class TestScenarioIDs:

    def test_no_duplicate_scenario_ids(self, all_scenarios_flat):
        """No duplicate scenario IDs across all classes."""
        ids = [s["id"] for _, s in all_scenarios_flat]
        duplicates = [x for x in ids if ids.count(x) > 1]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {set(duplicates)}"

    def test_ids_follow_naming_convention(self, all_scenarios_flat):
        """All IDs start with 'ATK-' prefix."""
        for cls, s in all_scenarios_flat:
            assert s["id"].startswith("ATK-"), (
                f"ID '{s['id']}' does not follow ATK-* naming convention"
            )


class TestAttackClassValidity:

    def test_all_classes_are_known(self, attack_scenarios):
        """All attack classes in scenarios are from the known taxonomy."""
        scenario_classes = set(attack_scenarios["attacks"].keys())
        unknown = scenario_classes - FULL_TAXONOMY_CLASSES
        assert not unknown, f"Unknown attack classes in scenarios: {unknown}"

    def test_implemented_classes_present(self, attack_scenarios):
        """All 5 implemented attack classes have scenarios."""
        scenario_classes = set(attack_scenarios["attacks"].keys())
        missing = IMPLEMENTED_CLASSES - scenario_classes
        assert not missing, f"Missing implemented classes: {missing}"


class TestScenarioCount:

    def test_total_scenario_count_matches_documentation(self, all_scenarios_flat):
        """FINDINGS.md documents 19 scenarios; verify that count.

        The 19 scenarios are across 5 implemented classes:
        prompt_injection (5), indirect_injection (4), tool_boundary (4),
        memory_poisoning (3), reasoning_hijack (3).
        """
        assert len(all_scenarios_flat) == 19, (
            f"Expected 19 scenarios (per FINDINGS.md), found {len(all_scenarios_flat)}"
        )

    def test_per_class_counts(self, attack_scenarios):
        """Per-class scenario counts match expected distribution."""
        expected = {
            "prompt_injection": 5,
            "indirect_injection": 4,
            "tool_boundary": 4,
            "memory_poisoning": 3,
            "reasoning_hijack": 3,
        }
        for cls, count in expected.items():
            actual = len(attack_scenarios["attacks"].get(cls, []))
            assert actual == count, (
                f"Class '{cls}': expected {count} scenarios, found {actual}"
            )
