#!/usr/bin/env python
"""Generate publication-ready figures from attack/defense JSON outputs.

Reads actual data from outputs/attacks/ and outputs/defenses/ summary JSONs.
No hardcoded values — all figures are derived from experimental data.

Produces:
  - figures/attack_success_rates.png    (bar chart: overall per-class, mean +/- std)
  - figures/defense_effectiveness.png   (grouped bar: each defense layer comparison)
  - figures/attack_by_class.png         (heatmap: class x seed success rate)

Usage:
    python scripts/generate_figures.py
    python scripts/generate_figures.py --output-dir outputs/figures
"""

import argparse
import json
import sys
from pathlib import Path
from glob import glob

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError:
    print("Required: pip install matplotlib numpy")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_attack_summaries(output_root: str = "outputs") -> list[dict]:
    """Load all attack summary JSONs from outputs/attacks/*/summary.json."""
    pattern = str(Path(output_root) / "attacks" / "*" / "summary.json")
    summaries = []
    for path in sorted(glob(pattern)):
        with open(path) as f:
            data = json.load(f)
        data["_path"] = path
        summaries.append(data)
    if not summaries:
        raise FileNotFoundError(f"No attack summaries found matching {pattern}")
    return summaries


def load_defense_summaries(output_root: str = "outputs") -> list[dict]:
    """Load all defense summary JSONs from outputs/defenses/*/summary.json."""
    pattern = str(Path(output_root) / "defenses" / "*" / "summary.json")
    summaries = []
    for path in sorted(glob(pattern)):
        with open(path) as f:
            data = json.load(f)
        data["_path"] = path
        summaries.append(data)
    if not summaries:
        raise FileNotFoundError(f"No defense summaries found matching {pattern}")
    return summaries


def get_langchain_all_attack_summaries(summaries: list[dict]) -> list[dict]:
    """Filter to langchain_react agent with attack_class='all' (full runs)."""
    return [
        s for s in summaries
        if s.get("agent") == "langchain_react" and s.get("attack_class") == "all"
    ]


def compute_class_stats(summaries: list[dict]) -> dict:
    """Compute per-class mean and std success rate across seeds.

    Returns: {class_name: {"mean": float, "std": float, "rates": [float, ...]}}
    """
    # Collect rates per class across all summaries
    class_rates: dict[str, list[float]] = {}
    for s in summaries:
        for cls, data in s.get("by_class", {}).items():
            rate = data.get("success_rate", 0)
            class_rates.setdefault(cls, []).append(rate)

    stats = {}
    for cls, rates in class_rates.items():
        arr = np.array(rates)
        stats[cls] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "rates": rates,
            "n_seeds": len(rates),
        }
    return stats


# ---------------------------------------------------------------------------
# Figure 1: Attack success rates (mean +/- std across seeds)
# ---------------------------------------------------------------------------

def fig_attack_success_rates(stats: dict, output_dir: str):
    """Bar chart: per-class attack success rates with error bars."""
    # Sort by mean rate descending
    ordered = sorted(stats.items(), key=lambda x: x[1]["mean"], reverse=True)
    class_names = [cls.replace("_", "\n") for cls, _ in ordered]
    means = [s["mean"] * 100 for _, s in ordered]
    stds = [s["std"] * 100 for _, s in ordered]
    n_seeds = ordered[0][1]["n_seeds"] if ordered else 0

    # Color by risk level
    colors = []
    for m in means:
        if m >= 90:
            colors.append("#e74c3c")  # Critical
        elif m > 50:
            colors.append("#e67e22")  # Demonstrated
        else:
            colors.append("#2ecc71")  # Not demonstrated

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(class_names, means, yerr=stds, capsize=5,
                  color=colors, edgecolor="#2c3e50", linewidth=1.2,
                  error_kw={"elinewidth": 1.5, "capthick": 1.5})

    ax.axhline(y=50, color="#e74c3c", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(len(class_names) - 0.5, 52, ">50% = demonstrated", fontsize=9,
            color="#e74c3c", ha="right", style="italic")

    for bar, mean, std in zip(bars, means, stds):
        label = f"{mean:.1f}%"
        if std > 0:
            label += f"\n+/-{std:.1f}"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + std + 2,
                label, ha="center", va="bottom", fontweight="bold", fontsize=10)

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title(
        f"Attack Success by Class (LangChain ReAct + Claude Sonnet, n={n_seeds} seeds)",
        fontsize=13, fontweight="bold"
    )
    ax.set_ylim(0, 120)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    legend_elements = [
        mpatches.Patch(facecolor="#e74c3c", label="Critical (>=90%)"),
        mpatches.Patch(facecolor="#e67e22", label="Demonstrated (>50%)"),
        mpatches.Patch(facecolor="#2ecc71", label="Not demonstrated (<=50%)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

    plt.tight_layout()
    out_path = Path(output_dir) / "attack_success_rates.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


# ---------------------------------------------------------------------------
# Figure 2: Defense effectiveness (grouped bar: no defense vs each defense)
# ---------------------------------------------------------------------------

def fig_defense_effectiveness(attack_stats: dict, defense_summaries: list[dict],
                               output_dir: str):
    """Grouped bar chart: baseline vs each defense layer."""
    # Filter to langchain_react defenses only
    lc_defenses = [
        s for s in defense_summaries
        if s.get("agent") == "langchain_react"
    ]

    if not lc_defenses:
        print("Warning: No LangChain defense summaries found, skipping defense figure.")
        return

    # Get class order from attack stats
    classes = sorted(attack_stats.keys())
    class_labels = [cls.replace("_", "\n") for cls in classes]

    # Baseline (no defense) rates
    baseline = [attack_stats[cls]["mean"] * 100 for cls in classes]

    # Gather defense data
    defense_data = {}
    for ds in lc_defenses:
        dname = ds["defense"]
        rates = []
        for cls in classes:
            cls_data = ds.get("by_class", {}).get(cls, {})
            rates.append(cls_data.get("success_rate", 0) * 100)
        defense_data[dname] = {
            "rates": rates,
            "avg_reduction": ds.get("average_reduction", 0),
        }

    # Plot: baseline + each defense as grouped bars
    n_groups = len(classes)
    n_bars = 1 + len(defense_data)
    width = 0.8 / n_bars
    x = np.arange(n_groups)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Baseline bars
    ax.bar(x - (n_bars - 1) * width / 2, baseline, width,
           label="No Defense", color="#e74c3c", edgecolor="#2c3e50", linewidth=0.8)

    # Defense bars
    defense_colors = {
        "input_sanitizer": "#3498db",
        "tool_boundary": "#9b59b6",
        "layered": "#2ecc71",
        "llm_judge": "#f39c12",
        "full": "#1abc9c",
    }

    for i, (dname, ddata) in enumerate(sorted(defense_data.items()), 1):
        color = defense_colors.get(dname, "#95a5a6")
        label = f"{dname} ({ddata['avg_reduction']:.0%} avg reduction)"
        ax.bar(x - (n_bars - 1) * width / 2 + i * width, ddata["rates"], width,
               label=label, color=color, edgecolor="#2c3e50", linewidth=0.8)

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title("Defense Effectiveness by Layer", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(class_labels)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=8, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    out_path = Path(output_dir) / "defense_effectiveness.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


# ---------------------------------------------------------------------------
# Figure 3: Attack by class heatmap (class x seed)
# ---------------------------------------------------------------------------

def fig_attack_by_class(summaries: list[dict], output_dir: str):
    """Heatmap: attack class x seed showing success rates."""
    if len(summaries) < 2:
        print("Warning: Need 2+ seeds for heatmap, skipping.")
        return

    # Build matrix: rows = classes, columns = seeds
    classes = sorted(
        set(cls for s in summaries for cls in s.get("by_class", {}).keys())
    )
    seeds = [s["seed"] for s in summaries]

    matrix = np.zeros((len(classes), len(seeds)))
    for j, s in enumerate(summaries):
        for i, cls in enumerate(classes):
            cls_data = s.get("by_class", {}).get(cls, {})
            matrix[i, j] = cls_data.get("success_rate", 0) * 100

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(matrix, cmap="RdYlGn_r", aspect="auto", vmin=0, vmax=100)

    # Labels
    ax.set_xticks(range(len(seeds)))
    ax.set_xticklabels([f"seed={s}" for s in seeds], fontsize=10)
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels([cls.replace("_", " ") for cls in classes], fontsize=10)

    # Annotate cells
    for i in range(len(classes)):
        for j in range(len(seeds)):
            val = matrix[i, j]
            color = "white" if val > 60 else "black"
            ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                    fontweight="bold", fontsize=11, color=color)

    # Mean column
    means = matrix.mean(axis=1)
    for i, m in enumerate(means):
        ax.text(len(seeds) + 0.3, i, f"mean={m:.1f}%", ha="left", va="center",
                fontsize=9, style="italic")

    ax.set_title("Attack Success Rate: Class x Seed",
                 fontsize=13, fontweight="bold")
    fig.colorbar(im, ax=ax, label="Success Rate (%)", shrink=0.8)

    plt.tight_layout()
    out_path = Path(output_dir) / "attack_by_class.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(out_path), dpi=150)
    plt.close()
    print(f"Generated: {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate figures from JSON outputs")
    parser.add_argument("--output-dir", default="outputs/figures",
                        help="Directory for output PNGs")
    parser.add_argument("--data-dir", default="outputs",
                        help="Root directory containing attacks/ and defenses/")
    args = parser.parse_args()

    print("Loading attack data...")
    all_attack_summaries = load_attack_summaries(args.data_dir)
    lc_summaries = get_langchain_all_attack_summaries(all_attack_summaries)
    print(f"  Found {len(all_attack_summaries)} total attack summaries")
    print(f"  Found {len(lc_summaries)} LangChain full-run summaries (seeds: {[s['seed'] for s in lc_summaries]})")

    print("\nLoading defense data...")
    defense_summaries = load_defense_summaries(args.data_dir)
    print(f"  Found {len(defense_summaries)} defense summaries")

    print("\nComputing statistics...")
    attack_stats = compute_class_stats(lc_summaries)
    for cls, s in sorted(attack_stats.items()):
        print(f"  {cls}: mean={s['mean']:.1%} std={s['std']:.1%} (n={s['n_seeds']})")

    print(f"\nGenerating figures to {args.output_dir}/...")
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    fig_attack_success_rates(attack_stats, args.output_dir)
    fig_defense_effectiveness(attack_stats, defense_summaries, args.output_dir)
    fig_attack_by_class(lc_summaries, args.output_dir)

    # Also copy to blog/images/ if it exists
    blog_dir = Path("blog/images")
    if blog_dir.exists():
        print(f"\nCopying to {blog_dir}/...")
        import shutil
        for png in Path(args.output_dir).glob("*.png"):
            shutil.copy2(png, blog_dir / png.name)
            print(f"  Copied: {png.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
