"""Tests for figure generation and data integrity.

Validates that figure generation script exists, existing PNGs are non-zero,
JSON data files exist, figure count matches expected, and no hardcoded
values appear in the generation script.

NO API calls. All tests operate on existing files.
"""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
FIGURES_DIR = ROOT / "outputs" / "figures"
BLOG_IMAGES_DIR = ROOT / "blog" / "images"
SCRIPT_PATH = ROOT / "scripts" / "generate_figures.py"
REPORT_SCRIPT_PATH = ROOT / "scripts" / "make_report_figures.py"

# Expected figures from FINDINGS.md: 3 generated figures + 2 pre-existing
EXPECTED_GENERATED = {
    "attack_success_rates.png",
    "defense_effectiveness.png",
    "attack_by_class.png",
}

EXPECTED_REPORT = {
    "report_attack_by_class.png",
    "report_defense_comparison.png",
    "report_seed_consistency.png",
    "report_framework_comparison.png",
}

EXPECTED_ALL_FIGURES = EXPECTED_GENERATED | EXPECTED_REPORT | {
    "controllability_analysis.png",
    "defense_comparison.png",
}


class TestFigureGenerationScript:

    def test_script_exists(self):
        """scripts/generate_figures.py exists."""
        assert SCRIPT_PATH.exists(), f"Missing: {SCRIPT_PATH}"

    def test_script_is_valid_python(self):
        """Script compiles as valid Python (syntax check)."""
        source = SCRIPT_PATH.read_text()
        compile(source, str(SCRIPT_PATH), "exec")

    def test_script_imports_json(self):
        """Script imports json module (reads data from files, not hardcoded)."""
        source = SCRIPT_PATH.read_text()
        assert "import json" in source

    def test_script_has_load_functions(self):
        """Script defines data loading functions."""
        source = SCRIPT_PATH.read_text()
        assert "def load_attack_summaries" in source
        assert "def load_defense_summaries" in source

    def test_script_has_main_entrypoint(self):
        """Script has a main() function and __name__ guard."""
        source = SCRIPT_PATH.read_text()
        assert "def main()" in source
        assert '__name__ == "__main__"' in source or "__name__ == '__main__'" in source


class TestReportFigureScript:

    def test_report_script_exists(self):
        """scripts/make_report_figures.py exists."""
        assert REPORT_SCRIPT_PATH.exists(), f"Missing: {REPORT_SCRIPT_PATH}"

    def test_report_script_is_valid_python(self):
        """Report script compiles as valid Python."""
        source = REPORT_SCRIPT_PATH.read_text()
        compile(source, str(REPORT_SCRIPT_PATH), "exec")

    def test_report_script_imports_json(self):
        """Report script imports json module."""
        source = REPORT_SCRIPT_PATH.read_text()
        assert "import json" in source

    def test_report_script_uses_agg_backend(self):
        """Report script uses Agg backend (no display needed)."""
        source = REPORT_SCRIPT_PATH.read_text()
        assert "Agg" in source

    def test_report_script_has_main(self):
        """Report script has main() and __name__ guard."""
        source = REPORT_SCRIPT_PATH.read_text()
        assert "def main()" in source
        assert '__name__ == "__main__"' in source

    def test_report_figures_exist(self):
        """All 4 report figures exist."""
        for name in EXPECTED_REPORT:
            path = FIGURES_DIR / name
            assert path.exists(), f"Missing report figure: {path}"


class TestExistingFigures:

    def test_figures_directory_exists(self):
        """outputs/figures/ directory exists."""
        assert FIGURES_DIR.exists(), f"Missing: {FIGURES_DIR}"

    def test_all_expected_figures_exist(self):
        """All 5 expected PNG figures exist."""
        for name in EXPECTED_ALL_FIGURES:
            path = FIGURES_DIR / name
            assert path.exists(), f"Missing figure: {path}"

    def test_figures_are_nonzero_size(self):
        """All PNG files are non-zero size (not empty/corrupt)."""
        for png in FIGURES_DIR.glob("*.png"):
            size = png.stat().st_size
            assert size > 0, f"Figure {png.name} is empty (0 bytes)"

    def test_figure_count_matches_expected(self):
        """Number of PNG files matches expected count."""
        pngs = list(FIGURES_DIR.glob("*.png"))
        assert len(pngs) == len(EXPECTED_ALL_FIGURES), (
            f"Expected {len(EXPECTED_ALL_FIGURES)} figures, "
            f"found {len(pngs)}: {[p.name for p in pngs]}"
        )

    def test_figures_are_reasonably_sized(self):
        """Figures are between 1KB and 5MB (sanity check)."""
        for png in FIGURES_DIR.glob("*.png"):
            size = png.stat().st_size
            assert size > 1024, (
                f"Figure {png.name} suspiciously small: {size} bytes"
            )
            assert size < 5 * 1024 * 1024, (
                f"Figure {png.name} suspiciously large: {size} bytes"
            )


class TestNoHardcodedValues:

    def test_no_hardcoded_rate_arrays(self):
        """Script does NOT contain hardcoded success rate arrays."""
        source = SCRIPT_PATH.read_text()
        # These patterns would indicate hardcoded data instead of reading JSON
        bad_patterns = [
            r"rates\s*=\s*\[[\d\.,\s]+\]",
            r"without\s*=\s*\[[\d\.,\s]+\]",
            r"with_defense\s*=\s*\[[\d\.,\s]+\]",
            r"baseline\s*=\s*\[\s*\d",
        ]
        for pattern in bad_patterns:
            match = re.search(pattern, source)
            assert match is None, (
                f"Hardcoded data found: '{match.group()}' — "
                f"script should read from JSON files"
            )

    def test_reads_from_json_files(self):
        """Script uses json.load to read data."""
        source = SCRIPT_PATH.read_text()
        assert "json.load" in source, (
            "Script should use json.load() to read output data"
        )

    def test_uses_glob_for_file_discovery(self):
        """Script uses glob pattern to discover output files."""
        source = SCRIPT_PATH.read_text()
        assert "glob" in source, (
            "Script should use glob to find summary.json files"
        )


class TestDataSourceFiles:

    def test_attack_json_files_exist(self):
        """JSON data files that feed figures exist."""
        attack_dir = ROOT / "outputs" / "attacks"
        assert attack_dir.exists()
        summaries = list(attack_dir.glob("*/summary.json"))
        assert len(summaries) >= 3, (
            f"Expected >=3 attack summary JSONs, found {len(summaries)}"
        )

    def test_defense_json_files_exist(self):
        """Defense JSON data files exist."""
        defense_dir = ROOT / "outputs" / "defenses"
        assert defense_dir.exists()
        summaries = list(defense_dir.glob("*/summary.json"))
        assert len(summaries) >= 2, (
            f"Expected >=2 defense summary JSONs, found {len(summaries)}"
        )

    def test_blog_images_directory_exists(self):
        """blog/images/ directory exists for publication copies."""
        assert BLOG_IMAGES_DIR.exists(), f"Missing: {BLOG_IMAGES_DIR}"

    def test_blog_images_match_generated(self):
        """Blog images directory contains copies of generated figures."""
        for name in EXPECTED_GENERATED:
            path = BLOG_IMAGES_DIR / name
            assert path.exists(), (
                f"Missing blog image: {name} — "
                f"run generate_figures.py to copy to blog/images/"
            )
