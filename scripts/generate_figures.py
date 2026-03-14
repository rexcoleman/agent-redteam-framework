#!/usr/bin/env python
"""Generate publication-ready figures from attack/defense results."""

import json
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("matplotlib not installed. Run: pip install matplotlib")
    exit(1)


def attack_success_chart():
    """Bar chart: attack success rates by class."""
    classes = [
        "Prompt\nInjection", "Tool\nBoundary", "Memory\nPoisoning",
        "Reasoning\nHijack", "Indirect\nInjection"
    ]
    rates = [80, 75, 67, 100, 25]
    colors = ["#e67e22", "#e67e22", "#e67e22", "#e74c3c", "#2ecc71"]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(classes, rates, color=colors, edgecolor="#2c3e50", linewidth=1.2)

    ax.axhline(y=50, color="#e74c3c", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(4.5, 52, ">50% = demonstrated", fontsize=9, color="#e74c3c",
            ha="right", style="italic")

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f"{rate}%", ha="center", va="bottom", fontweight="bold", fontsize=12)

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title("Attack Success by Class (LangChain ReAct + Claude Sonnet, seed=42)",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    legend_elements = [
        mpatches.Patch(facecolor="#e74c3c", label="Highest risk (100%)"),
        mpatches.Patch(facecolor="#e67e22", label="Demonstrated (>50%)"),
        mpatches.Patch(facecolor="#2ecc71", label="Not demonstrated (<50%)"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=9)

    plt.tight_layout()
    plt.savefig("outputs/figures/attack_success_rates.png", dpi=150)
    plt.savefig("blog/images/attack_success_rates.png", dpi=150)
    print("Generated: attack_success_rates.png")


def defense_comparison_chart():
    """Grouped bar chart: before/after defense."""
    classes = [
        "Prompt\nInjection", "Tool\nBoundary", "Memory\nPoisoning",
        "Reasoning\nHijack", "Indirect\nInjection"
    ]
    without = [80, 75, 67, 100, 25]
    with_defense = [0, 25, 0, 67, 25]

    import numpy as np
    x = np.arange(len(classes))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, without, width, label="No Defense",
                   color="#e74c3c", edgecolor="#2c3e50", linewidth=1)
    bars2 = ax.bar(x + width/2, with_defense, width, label="Layered Defense",
                   color="#3498db", edgecolor="#2c3e50", linewidth=1)

    for bar, rate in zip(bars1, without):
        if rate > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f"{rate}%", ha="center", va="bottom", fontsize=10, color="#e74c3c")

    for bar, rate in zip(bars2, with_defense):
        ax.text(bar.get_x() + bar.get_width()/2, max(rate, 0) + 2,
                f"{rate}%", ha="center", va="bottom", fontsize=10, color="#3498db")

    # Reduction annotations
    reductions = [100, 67, 100, 33, 0]
    for i, red in enumerate(reductions):
        if red > 0:
            ax.annotate(f"-{red}%", xy=(x[i], max(without[i], with_defense[i]) + 10),
                       fontsize=9, ha="center", color="#27ae60", fontweight="bold")

    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title("Defense Effectiveness: Layered Defense (Input Sanitizer + Tool Boundary)",
                 fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.set_ylim(0, 125)
    ax.legend(fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Average reduction callout
    ax.text(0.98, 0.95, "Average reduction: 60%",
            transform=ax.transAxes, fontsize=12, fontweight="bold",
            ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#27ae60", alpha=0.3))

    plt.tight_layout()
    plt.savefig("outputs/figures/defense_comparison.png", dpi=150)
    plt.savefig("blog/images/defense_comparison.png", dpi=150)
    print("Generated: defense_comparison.png")


def controllability_chart():
    """Scatter plot: observability vs attack success."""
    labels = [
        "User Prompt", "Tool Params", "Conv. History",
        "Tool Outputs", "Reasoning Chain"
    ]
    observability = [5, 4, 2.5, 2, 0.5]  # 5=high, 0=none
    success = [80, 75, 67, 25, 100]
    colors = ["#e67e22", "#e67e22", "#f39c12", "#2ecc71", "#e74c3c"]
    sizes = [s * 3 for s in success]

    fig, ax = plt.subplots(figsize=(9, 6))
    scatter = ax.scatter(observability, success, c=colors, s=sizes,
                        edgecolors="#2c3e50", linewidth=1.5, zorder=5)

    for i, label in enumerate(labels):
        offset_y = 5 if label != "Tool Outputs" else -8
        ax.annotate(label, (observability[i], success[i]),
                   textcoords="offset points", xytext=(10, offset_y),
                   fontsize=10, fontweight="bold")

    # Trend line
    import numpy as np
    z = np.polyfit(observability, success, 1)
    p = np.poly1d(z)
    x_line = np.linspace(0, 5.5, 100)
    ax.plot(x_line, p(x_line), "--", color="#95a5a6", alpha=0.5, linewidth=1.5)

    ax.set_xlabel("Defender Observability →", fontsize=12)
    ax.set_ylabel("Attack Success Rate (%)", fontsize=12)
    ax.set_title("Controllability Analysis: Observability vs. Attack Success",
                 fontsize=13, fontweight="bold")
    ax.set_xlim(-0.2, 5.8)
    ax.set_ylim(0, 115)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.text(0.02, 0.98, "Less observable → more vulnerable",
            transform=ax.transAxes, fontsize=10, style="italic",
            va="top", color="#7f8c8d")

    plt.tight_layout()
    plt.savefig("outputs/figures/controllability_analysis.png", dpi=150)
    plt.savefig("blog/images/controllability_analysis.png", dpi=150)
    print("Generated: controllability_analysis.png")


if __name__ == "__main__":
    print("Generating FP-02 figures...")
    attack_success_chart()
    defense_comparison_chart()
    controllability_chart()
    print("Done. Figures in outputs/figures/ and blog/images/")
