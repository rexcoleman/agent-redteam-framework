#!/usr/bin/env python
"""Generate report figures from attack/defense JSON outputs.

Reads actual data from outputs/attacks/ and outputs/defenses/ summary JSONs.
No hardcoded values -- all figures are derived from experimental data.

Produces:
  - outputs/figures/report_attack_by_class.png       (bar: per-class success rates)
  - outputs/figures/report_defense_comparison.png     (grouped bar: no defense vs layered vs full)
  - outputs/figures/report_seed_consistency.png       (grouped bar: per-class rates across seeds)
  - outputs/figures/report_framework_comparison.png   (grouped bar: LangChain vs CrewAI)

Usage:
    python scripts/make_report_figures.py
    python scripts/make_report_figures.py --output-dir outputs/figures
    python scripts/make_report_figures.py --data-dir outputs
"""

import argparse
import json
import sys
from pathlib import Path
from glob import glob

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Required: pip install matplotlib numpy")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
PALETTE = {
    "red": "#e74c3c",
    "orange": "#e67e22",
    "green": "#2ecc71",
    "blue": "#3498db",
    "purple": "#9b59b6",
    "teal": "#1abc9c",
    "dark": "#2c3e50",
    "gray": "#95a5a6",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_summaries(output_root: str, subdir: str) -> list[dict]:
    """Load all summary.json files from outputs/<subdir>/*/summary.json."""
    pattern = str(Path(output_root) / subdir / "*" / "summary.json")
    summaries = []
    for path in sorted(glob(pattern)):
        with open(path) as f:
            data = json.load(f)
        data["_path"] = path
        summaries.append(data)
    return summaries


def filter_langchain_all(summaries: list[dict]) -> list[dict]:
    """Filter to langchain_react agent with attack_class='all' (full runs)."""
    return [
        s for s in summaries
        if s.get("agent") == "langchain_react" and s.get("attack_class") == "all"
    ]


# ---------------------------------------------------------------------------
# Figure 1: Attack success rates by class
# ---------------------------------------------------------------------------

def fig_attack_by_class(summaries: list[dict], output_dir: str):
    """Bar chart showing mean attack success rate per class across seeds."""
    if not summaries:
        print("  SKIP: No LangChain full-run summaries found.")
        return

    # Collect per-class rates across seeds
    class_rates: dict[str, list[float]] = {}
    for s in summaries:
        for cls, data in s.get("by_class", {}).items():
            class_rates.setdefault(cls, []).append(data.get("success_rate", 0))

    # Sort by mean descending
    stats = {
        cls: {"mean": np.mean(rates), "std": np.std(rates), "n": len(rates)}
        for cls, rates in class_rates.items()
    }
    ordered = sorted(stats.items(), key=lambda x: x[1]["mean"], reverse=True)

    labels = [cls.replace("_", " ").title() for cls, _ in ordered]
    means = [s["mean"] * 100 for _, s in ordered]
    stds = [s["std"] * 100 for _, s in ordered]
    n_seeds = ordered[0][1]["n"] if ordered else 0

    colors = []
    for m in means:
        if m >= 90:
            colors.append(PALETTE["red"])
        elif m > 50:
            colors.append(PALETTE["orange"])
        else:
            colors.append(PALETTE["green"])

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, means, yerr=stds, capsize=5,
                  color=colors, edgecolor=PALETTE["dark"], linewidth=1.2,
                  error_kw={"elinewidth": 1.5, "capthick": 1.5})

    ax.axhline(y=50, color=PALETTE["red"], linestyle="--", linewidth=1, alpha=0.6)
    ax.text(len(labels) - 0.5, 52, ">50% = demonstrated", fontsize=9,
            color=PALETTE["red"], ha="right", style="italic")

    for bar, mean_val, std_val in zip(bars, means, stds):
        label = f"{mean_val:.1f}%"
        if std_val > 0:
            label += f"\n({std_val:.1f})"
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + std_val + 2,
                label, ha="center", va="bottom", fontweight="bold", fontsize=10)

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title(
        f"Attack Success by Class (LangChain ReAct, n={n_seeds} seeds)",
        fontsize=13, fontweight="bold",
    )
    ax.set_ylim(0, 120)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = Path(output_dir) / "report_attack_by_class.png"
    plt.savefig(str(out), dpi=150)
    plt.close()
    print(f"  Generated: {out}")


# ---------------------------------------------------------------------------
# Figure 2: Defense effectiveness comparison
# ---------------------------------------------------------------------------

def fig_defense_comparison(attack_summaries: list[dict],
                           defense_summaries: list[dict],
                           output_dir: str):
    """Grouped bar chart: no defense vs layered vs full defense."""
    lc_attacks = filter_langchain_all(attack_summaries)
    if not lc_attacks:
        print("  SKIP: No LangChain attack summaries.")
        return

    # Compute baseline per-class means
    class_rates: dict[str, list[float]] = {}
    for s in lc_attacks:
        for cls, data in s.get("by_class", {}).items():
            class_rates.setdefault(cls, []).append(data.get("success_rate", 0))
    baseline_means = {cls: np.mean(rates) for cls, rates in class_rates.items()}

    # Select layered and full defenses
    target_defenses = {}
    for ds in defense_summaries:
        dname = ds.get("defense", "")
        if dname in ("layered", "full") and ds.get("agent") == "langchain_react":
            target_defenses[dname] = ds

    if not target_defenses:
        print("  SKIP: No layered/full defense summaries found.")
        return

    classes = sorted(baseline_means.keys())
    class_labels = [cls.replace("_", " ").title() for cls in classes]

    no_def = [baseline_means[cls] * 100 for cls in classes]

    x = np.arange(len(classes))
    n_bars = 1 + len(target_defenses)
    width = 0.8 / n_bars

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(x - (n_bars - 1) * width / 2, no_def, width,
           label="No Defense", color=PALETTE["red"],
           edgecolor=PALETTE["dark"], linewidth=0.8)

    defense_colors = {"layered": PALETTE["green"], "full": PALETTE["teal"]}
    for i, dname in enumerate(["layered", "full"], 1):
        if dname not in target_defenses:
            continue
        ds = target_defenses[dname]
        rates = []
        for cls in classes:
            cls_data = ds.get("by_class", {}).get(cls, {})
            rates.append(cls_data.get("success_rate", 0) * 100)
        reduction = ds.get("average_reduction", 0)
        ax.bar(x - (n_bars - 1) * width / 2 + i * width, rates, width,
               label=f"{dname.title()} ({reduction:.0%} avg reduction)",
               color=defense_colors.get(dname, PALETTE["gray"]),
               edgecolor=PALETTE["dark"], linewidth=0.8)

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title("Defense Effectiveness: No Defense vs Layered vs Full",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(class_labels)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=9, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = Path(output_dir) / "report_defense_comparison.png"
    plt.savefig(str(out), dpi=150)
    plt.close()
    print(f"  Generated: {out}")


# ---------------------------------------------------------------------------
# Figure 3: Attack success by seed (consistency)
# ---------------------------------------------------------------------------

def fig_seed_consistency(summaries: list[dict], output_dir: str):
    """Grouped bar chart: per-class success rates across seeds."""
    if len(summaries) < 2:
        print("  SKIP: Need >= 2 seeds for consistency plot.")
        return

    classes = sorted(
        set(cls for s in summaries for cls in s.get("by_class", {}).keys())
    )
    seeds = [s["seed"] for s in summaries]
    class_labels = [cls.replace("_", " ").title() for cls in classes]

    x = np.arange(len(classes))
    n_bars = len(seeds)
    width = 0.8 / n_bars
    seed_colors = [PALETTE["blue"], PALETTE["orange"], PALETTE["purple"]]

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, (s, seed) in enumerate(zip(summaries, seeds)):
        rates = []
        for cls in classes:
            cls_data = s.get("by_class", {}).get(cls, {})
            rates.append(cls_data.get("success_rate", 0) * 100)
        color = seed_colors[i % len(seed_colors)]
        ax.bar(x - (n_bars - 1) * width / 2 + i * width, rates, width,
               label=f"seed={seed}", color=color,
               edgecolor=PALETTE["dark"], linewidth=0.8)

    # Annotate per-class std
    for j, cls in enumerate(classes):
        vals = []
        for s in summaries:
            cls_data = s.get("by_class", {}).get(cls, {})
            vals.append(cls_data.get("success_rate", 0) * 100)
        std = np.std(vals)
        if std > 0:
            ax.text(j, max(vals) + 3, f"sd={std:.1f}", ha="center",
                    fontsize=8, style="italic", color=PALETTE["dark"])

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title("Cross-Seed Consistency of Attack Success Rates",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(class_labels)
    ax.set_ylim(0, 120)
    ax.legend(fontsize=9, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = Path(output_dir) / "report_seed_consistency.png"
    plt.savefig(str(out), dpi=150)
    plt.close()
    print(f"  Generated: {out}")


# ---------------------------------------------------------------------------
# Figure 4: Framework comparison (LangChain vs CrewAI)
# ---------------------------------------------------------------------------

def fig_framework_comparison(attack_summaries: list[dict], output_dir: str):
    """Grouped bar chart comparing LangChain and CrewAI on overlapping attack classes."""
    # Group by framework
    lc_runs = [s for s in attack_summaries
               if s.get("agent") == "langchain_react" and s.get("attack_class") == "all"]
    crewai_runs = [s for s in attack_summaries
                   if "crewai" in s.get("agent", "")]

    if not lc_runs or not crewai_runs:
        print("  SKIP: Need both LangChain and CrewAI data for framework comparison.")
        return

    # Determine overlapping attack classes
    lc_classes = set()
    for s in lc_runs:
        lc_classes.update(s.get("by_class", {}).keys())

    crewai_classes = set()
    for s in crewai_runs:
        crewai_classes.update(s.get("by_class", {}).keys())

    common_classes = sorted(lc_classes & crewai_classes)
    if not common_classes:
        # Also show classes unique to each
        all_classes = sorted(lc_classes | crewai_classes)
        common_classes = all_classes

    class_labels = [cls.replace("_", " ").title() for cls in common_classes]

    # Compute mean rates per class per framework
    def mean_rate(runs, cls):
        rates = []
        for s in runs:
            cls_data = s.get("by_class", {}).get(cls, {})
            rates.append(cls_data.get("success_rate", 0))
        return np.mean(rates) * 100 if rates else 0

    lc_rates = [mean_rate(lc_runs, cls) for cls in common_classes]
    crewai_rates = [mean_rate(crewai_runs, cls) for cls in common_classes]

    x = np.arange(len(common_classes))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, lc_rates, width,
           label=f"LangChain ReAct (n={len(lc_runs)} runs)",
           color=PALETTE["blue"], edgecolor=PALETTE["dark"], linewidth=0.8)
    ax.bar(x + width / 2, crewai_rates, width,
           label=f"CrewAI Multi-Agent (n={len(crewai_runs)} runs)",
           color=PALETTE["purple"], edgecolor=PALETTE["dark"], linewidth=0.8)

    # Value labels
    for xi, lc_val, cr_val in zip(x, lc_rates, crewai_rates):
        if lc_val > 0:
            ax.text(xi - width / 2, lc_val + 2, f"{lc_val:.0f}%",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
        if cr_val > 0:
            ax.text(xi + width / 2, cr_val + 2, f"{cr_val:.0f}%",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title("Framework Comparison: LangChain vs CrewAI",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(class_labels)
    ax.set_ylim(0, 120)
    ax.legend(fontsize=9, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out = Path(output_dir) / "report_framework_comparison.png"
    plt.savefig(str(out), dpi=150)
    plt.close()
    print(f"  Generated: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate report figures from JSON outputs"
    )
    parser.add_argument("--output-dir", default="outputs/figures",
                        help="Directory for output PNGs")
    parser.add_argument("--data-dir", default="outputs",
                        help="Root directory containing attacks/ and defenses/")
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    print("Loading data...")
    attack_summaries = load_summaries(args.data_dir, "attacks")
    defense_summaries = load_summaries(args.data_dir, "defenses")
    lc_all = filter_langchain_all(attack_summaries)
    print(f"  {len(attack_summaries)} attack summaries "
          f"({len(lc_all)} LangChain full-run, seeds: {[s['seed'] for s in lc_all]})")
    print(f"  {len(defense_summaries)} defense summaries")

    print(f"\nGenerating figures to {args.output_dir}/...")

    fig_attack_by_class(lc_all, args.output_dir)
    fig_defense_comparison(attack_summaries, defense_summaries, args.output_dir)
    fig_seed_consistency(lc_all, args.output_dir)
    fig_framework_comparison(attack_summaries, args.output_dir)

    print("\nDone. 4 report figures generated.")


if __name__ == "__main__":
    main()
