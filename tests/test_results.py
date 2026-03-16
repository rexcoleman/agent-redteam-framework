"""Tests for result JSON file integrity.

Validates that result files have required fields, success rates are correct,
multi-seed results exist, all attack classes have results, and no invalid
rate values appear.

NO API calls. All tests operate on existing JSON output files.
"""
import json
import sys
from glob import glob
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
ATTACKS_DIR = ROOT / "outputs" / "attacks"
DEFENSES_DIR = ROOT / "outputs" / "defenses"

# Expected attack classes in full-run results
EXPECTED_CLASSES = {
    "prompt_injection",
    "indirect_injection",
    "tool_boundary",
    "memory_poisoning",
    "reasoning_hijack",
}


@pytest.fixture
def langchain_attack_summaries():
    """Load all LangChain full-run attack summary JSONs."""
    pattern = str(ATTACKS_DIR / "langchain_react_all_seed*" / "summary.json")
    summaries = []
    for path in sorted(glob(pattern)):
        with open(path) as f:
            data = json.load(f)
        data["_path"] = path
        summaries.append(data)
    return summaries


@pytest.fixture
def all_attack_summaries():
    """Load all attack summary JSONs (including CrewAI)."""
    pattern = str(ATTACKS_DIR / "*" / "summary.json")
    summaries = []
    for path in sorted(glob(pattern)):
        with open(path) as f:
            data = json.load(f)
        data["_path"] = path
        summaries.append(data)
    return summaries


@pytest.fixture
def defense_summaries():
    """Load all defense summary JSONs."""
    pattern = str(DEFENSES_DIR / "*" / "summary.json")
    summaries = []
    for path in sorted(glob(pattern)):
        with open(path) as f:
            data = json.load(f)
        data["_path"] = path
        summaries.append(data)
    return summaries


class TestResultRequiredFields:

    def test_attack_summaries_have_seed(self, all_attack_summaries):
        """Every attack summary has a 'seed' field."""
        for s in all_attack_summaries:
            assert "seed" in s, f"Missing 'seed' in {s['_path']}"

    def test_attack_summaries_have_by_class(self, all_attack_summaries):
        """Every attack summary has 'by_class' with per-class results."""
        for s in all_attack_summaries:
            assert "by_class" in s, f"Missing 'by_class' in {s['_path']}"
            assert len(s["by_class"]) >= 1, f"Empty 'by_class' in {s['_path']}"

    def test_per_class_has_success_rate_and_total(self, all_attack_summaries):
        """Each class entry has 'success_rate' and 'total'."""
        for s in all_attack_summaries:
            for cls, data in s["by_class"].items():
                assert "success_rate" in data, (
                    f"Missing success_rate for {cls} in {s['_path']}"
                )
                assert "total" in data, (
                    f"Missing total for {cls} in {s['_path']}"
                )

    def test_attack_summaries_have_agent_field(self, all_attack_summaries):
        """Every attack summary specifies which agent was used."""
        for s in all_attack_summaries:
            assert "agent" in s, f"Missing 'agent' in {s['_path']}"

    def test_defense_summaries_have_defense_field(self, defense_summaries):
        """Every defense summary specifies which defense was active."""
        for s in defense_summaries:
            assert "defense" in s, f"Missing 'defense' in {s['_path']}"


class TestSuccessRateCalculations:

    def test_success_rate_equals_success_over_total(self, langchain_attack_summaries):
        """success_rate = success / total for each class."""
        for s in langchain_attack_summaries:
            for cls, data in s["by_class"].items():
                if data["total"] > 0:
                    expected = data["success"] / data["total"]
                    assert abs(data["success_rate"] - expected) < 1e-9, (
                        f"Incorrect success_rate for {cls} in seed {s['seed']}: "
                        f"{data['success_rate']} != {data['success']}/{data['total']}"
                    )

    def test_no_success_rate_above_one(self, all_attack_summaries):
        """No success rate exceeds 1.0."""
        for s in all_attack_summaries:
            for cls, data in s["by_class"].items():
                assert data["success_rate"] <= 1.0, (
                    f"success_rate > 1.0 for {cls} in {s['_path']}: {data['success_rate']}"
                )

    def test_no_success_rate_below_zero(self, all_attack_summaries):
        """No success rate is negative."""
        for s in all_attack_summaries:
            for cls, data in s["by_class"].items():
                assert data["success_rate"] >= 0.0, (
                    f"success_rate < 0.0 for {cls} in {s['_path']}: {data['success_rate']}"
                )

    def test_defense_reduction_is_valid(self, defense_summaries):
        """Defense average_reduction is between 0 and 1."""
        for s in defense_summaries:
            if "average_reduction" in s:
                assert 0.0 <= s["average_reduction"] <= 1.0, (
                    f"Invalid average_reduction in {s['_path']}: {s['average_reduction']}"
                )


class TestMultiSeed:

    def test_at_least_three_seeds(self, langchain_attack_summaries):
        """LangChain full-run results exist for at least 3 seeds."""
        seeds = [s["seed"] for s in langchain_attack_summaries]
        assert len(seeds) >= 3, (
            f"Expected >=3 seeds, found {len(seeds)}: {seeds}"
        )

    def test_seeds_are_42_123_456(self, langchain_attack_summaries):
        """Expected seeds are 42, 123, 456."""
        seeds = sorted(s["seed"] for s in langchain_attack_summaries)
        assert seeds == [42, 123, 456], f"Unexpected seeds: {seeds}"

    def test_results_consistent_across_seeds(self, langchain_attack_summaries):
        """Results are broadly consistent across seeds (same classes present)."""
        class_sets = []
        for s in langchain_attack_summaries:
            class_sets.append(set(s["by_class"].keys()))
        # All seeds should have the same attack classes
        for i, cs in enumerate(class_sets[1:], 1):
            assert cs == class_sets[0], (
                f"Seed {langchain_attack_summaries[i]['seed']} has different "
                f"classes than seed {langchain_attack_summaries[0]['seed']}"
            )


class TestAttackClassCoverage:

    def test_all_classes_have_results(self, langchain_attack_summaries):
        """All 5 implemented attack classes appear in at least one result."""
        all_classes = set()
        for s in langchain_attack_summaries:
            all_classes.update(s["by_class"].keys())
        missing = EXPECTED_CLASSES - all_classes
        assert not missing, f"Attack classes with no results: {missing}"

    def test_crewai_results_exist(self, all_attack_summaries):
        """At least one CrewAI attack result exists."""
        crewai = [s for s in all_attack_summaries if s.get("agent") == "crewai_multi"]
        assert len(crewai) >= 1, "No CrewAI attack results found"

    def test_outcomes_list_present(self, langchain_attack_summaries):
        """Full-run summaries include an 'outcomes' list with per-scenario results."""
        for s in langchain_attack_summaries:
            assert "outcomes" in s, f"Missing 'outcomes' in seed {s['seed']}"
            assert len(s["outcomes"]) >= 15, (
                f"Expected >=15 outcomes in seed {s['seed']}, "
                f"found {len(s['outcomes'])}"
            )
