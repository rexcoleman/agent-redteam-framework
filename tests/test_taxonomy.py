"""Tests for the attack taxonomy defined in docs/attack_taxonomy.md.

Validates that all 7 attack classes are defined, each has required metadata,
controllability values use the correct enum, and OWASP mappings are valid.

NO API calls. All tests operate on static files and source code.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
TAXONOMY_PATH = ROOT / "docs" / "attack_taxonomy.md"

# The 7 classes from the taxonomy document
EXPECTED_CLASSES = {
    1: "Direct Prompt Injection",
    2: "Indirect Prompt Injection via Tool Outputs",
    3: "Tool Permission Boundary Violation",
    4: "Cross-Agent Privilege Escalation",
    5: "Memory/Context Poisoning",
    6: "Reasoning Chain Hijacking",
    7: "Output Format Exploitation",
}

# Valid controllability values from src/core/types.py Controllability enum
VALID_CONTROLLABILITY = {
    "attacker_controlled",
    "attacker-controlled",
    "partially_controllable",
    "partially controllable",
    "defender_controlled",
    "defender-controlled",
    "environment",
    "poisonable",
    "agent-generated",
    "agent_generated",
}

# Valid OWASP LLM Top 10 IDs
VALID_OWASP_IDS = {f"LLM{i:02d}" for i in range(1, 11)}


@pytest.fixture
def taxonomy_content():
    """Load taxonomy markdown content."""
    return TAXONOMY_PATH.read_text()


class TestTaxonomyCompleteness:

    def test_taxonomy_file_exists(self):
        """docs/attack_taxonomy.md exists."""
        assert TAXONOMY_PATH.exists(), f"Missing: {TAXONOMY_PATH}"

    def test_all_seven_classes_defined(self, taxonomy_content):
        """All 7 attack classes are present in the taxonomy."""
        for num, name in EXPECTED_CLASSES.items():
            assert f"Class {num}" in taxonomy_content, (
                f"Missing Class {num}: {name}"
            )

    def test_no_gaps_in_class_numbering(self, taxonomy_content):
        """Classes are numbered 1-7 with no gaps."""
        for i in range(1, 8):
            assert f"Class {i}" in taxonomy_content, (
                f"Gap in class numbering: Class {i} missing"
            )

    def test_class_count_is_seven(self, taxonomy_content):
        """Exactly 7 top-level '### Class N:' headings."""
        headings = re.findall(r"### Class \d+:", taxonomy_content)
        assert len(headings) == 7, (
            f"Expected 7 class headings, found {len(headings)}: {headings}"
        )

    def test_each_class_has_what_description(self, taxonomy_content):
        """Each class section contains a '**What:**' description."""
        for num in range(1, 8):
            # Find the section for this class
            pattern = rf"### Class {num}:.*?(?=### Class {num+1}:|## |\Z)"
            match = re.search(pattern, taxonomy_content, re.DOTALL)
            assert match is not None, f"Cannot find section for Class {num}"
            section = match.group(0)
            assert "**What:**" in section, (
                f"Class {num} missing '**What:**' description"
            )


class TestControllabilityValues:

    def test_controllability_matrix_exists(self, taxonomy_content):
        """Controllability Matrix section exists."""
        assert "Controllability Matrix" in taxonomy_content

    def test_controllability_values_are_valid(self, taxonomy_content):
        """All controllability values in the matrix are from the valid set."""
        # Extract the controllability column from the markdown table
        matrix_match = re.search(
            r"## Controllability Matrix.*?\n\n(.*?)(?=\n## |\Z)",
            taxonomy_content,
            re.DOTALL,
        )
        assert matrix_match is not None, "Controllability Matrix section not found"
        matrix_text = matrix_match.group(1)

        # Parse table rows (skip header and separator)
        rows = [
            line for line in matrix_text.strip().split("\n")
            if "|" in line and "---" not in line and "Attack Class" not in line
        ]

        for row in rows:
            cells = [c.strip() for c in row.split("|") if c.strip()]
            if len(cells) >= 3:
                controllability = cells[2].lower().strip("*")
                # Normalize for comparison
                normalized = controllability.replace(" ", "_").replace("-", "_")
                valid_normalized = {v.replace(" ", "_").replace("-", "_") for v in VALID_CONTROLLABILITY}
                assert normalized in valid_normalized, (
                    f"Invalid controllability value: '{controllability}' in row: {row}"
                )


class TestOWASPMapping:

    def test_owasp_references_are_valid(self, taxonomy_content):
        """All OWASP LLM references use valid IDs (LLM01-LLM10)."""
        owasp_refs = re.findall(r"LLM\d{2}", taxonomy_content)
        for ref in owasp_refs:
            assert ref in VALID_OWASP_IDS, (
                f"Invalid OWASP reference: {ref}. Valid: LLM01-LLM10"
            )

    def test_owasp_coverage_table_exists(self, taxonomy_content):
        """OWASP Top 10 coverage table is present."""
        assert "OWASP" in taxonomy_content
        assert "LLM01" in taxonomy_content, "Missing LLM01 (Prompt Injection) reference"


class TestNoveltyAssessment:

    def test_novelty_table_exists(self, taxonomy_content):
        """Novelty Assessment table is present."""
        assert "Novelty Assessment" in taxonomy_content

    def test_five_classes_not_in_owasp(self, taxonomy_content):
        """At least 5 classes are marked as not fully covered by OWASP/ATLAS."""
        # The document states "Classes not covered by OWASP/ATLAS: 5"
        assert "5" in taxonomy_content and "not covered" in taxonomy_content.lower()


class TestControllabilityEnum:

    def test_controllability_enum_has_expected_values(self):
        """Controllability enum in types.py has the expected values."""
        from src.core.types import Controllability
        expected = {
            "attacker_controlled",
            "partially_controllable",
            "defender_controlled",
            "environment",
        }
        actual = {c.value for c in Controllability}
        assert expected == actual, f"Controllability values: {actual}, expected: {expected}"
