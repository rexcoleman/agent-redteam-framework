"""CLI entry point for agent-redteam framework.

Usage:
    agent-redteam scan --agent langchain_react --attack all --seed 42
    agent-redteam baseline --agent langchain_react --seed 42
    agent-redteam defend --agent langchain_react --defense layered --seed 42
    agent-redteam verify-env
"""

import click
import subprocess
import sys


@click.group()
@click.version_option(version="0.1.0", prog_name="agent-redteam")
def cli():
    """Agent Security Red-Team Framework — systematically discover vulnerabilities in AI agents."""
    pass


@cli.command()
@click.option("--agent", default="langchain_react", help="Agent target (langchain_react, crewai_multi)")
@click.option("--attack", default="all", help="Attack class or 'all'")
@click.option("--seed", default=42, type=int, help="Random seed")
@click.option("--dry-run", is_flag=True, help="Skip API calls")
def scan(agent, attack, seed, dry_run):
    """Run attack scenarios against an agent target."""
    cmd = [sys.executable, "scripts/run_attacks.py",
           "--agent", agent, "--attack", attack, "--seed", str(seed)]
    if dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, check=True)


@cli.command()
@click.option("--agent", default="langchain_react")
@click.option("--seed", default=42, type=int)
@click.option("--task", default=None, help="Specific task ID")
@click.option("--dry-run", is_flag=True)
def baseline(agent, seed, task, dry_run):
    """Capture baseline agent behavior on benign tasks."""
    cmd = [sys.executable, "scripts/run_baselines.py",
           "--agent", agent, "--seed", str(seed)]
    if task:
        cmd.extend(["--task", task])
    if dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, check=True)


@cli.command()
@click.option("--agent", default="langchain_react")
@click.option("--defense", default="layered", help="Defense (input_sanitizer, tool_boundary, layered)")
@click.option("--seed", default=42, type=int)
@click.option("--dry-run", is_flag=True)
def defend(agent, defense, seed, dry_run):
    """Evaluate defenses against attacks."""
    cmd = [sys.executable, "scripts/run_defenses.py",
           "--agent", agent, "--defense", defense, "--seed", str(seed)]
    if dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, check=True)


@cli.command(name="verify-env")
def verify_env():
    """Verify environment and framework imports."""
    subprocess.run(["bash", "scripts/verify_env.sh"], check=True)


@cli.command()
def figures():
    """Generate publication-ready figures from results."""
    subprocess.run([sys.executable, "scripts/generate_figures.py"], check=True)


if __name__ == "__main__":
    cli()
