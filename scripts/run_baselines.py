#!/usr/bin/env python
"""Phase 1: Capture baseline agent behavior on benign tasks.

Usage:
    python scripts/run_baselines.py --agent langchain_react --seed 42
    python scripts/run_baselines.py --agent langchain_react --task BL-001 --seed 42
    python scripts/run_baselines.py --dry-run
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import load_config, get_llm_config, get_agent_config
from src.core.logging import setup_logger, write_summary_json
from src.core.types import AgentResponse


def load_tasks(task_file: str = "data/tasks/baseline_tasks.yaml") -> list[dict]:
    with open(task_file) as f:
        return yaml.safe_load(f)["tasks"]


def create_agent(agent_name: str, config: dict, llm_config: dict):
    """Factory: create agent target by name."""
    if agent_name == "langchain_react":
        from src.agents.langchain_target import LangChainReActTarget
        agent_config = get_agent_config(config, agent_name)
        return LangChainReActTarget(config=agent_config, llm_config=llm_config)
    else:
        raise ValueError(f"Agent '{agent_name}' not yet implemented. Available: langchain_react")


def run_baselines(agent_name: str, seed: int, task_id: str | None = None, dry_run: bool = False):
    config = load_config()
    llm_config = get_llm_config(config)
    logger = setup_logger("baselines", output_dir=f"outputs/baselines/{agent_name}_seed{seed}")

    tasks = load_tasks()
    if task_id:
        tasks = [t for t in tasks if t["id"] == task_id]
        if not tasks:
            print(f"Task {task_id} not found.")
            sys.exit(1)

    print(f"Running {len(tasks)} baseline tasks on {agent_name} (seed={seed})")

    if dry_run:
        for task in tasks:
            print(f"  [dry-run] {task['id']}: {task['description']}")
        print(f"\n[dry-run] Would run {len(tasks)} tasks. No API calls made.")
        return

    agent = create_agent(agent_name, config, llm_config)
    agent.setup()

    results = []
    total_cost = 0.0

    for task in tasks:
        print(f"\n--- {task['id']}: {task['description']} ---")
        agent.reset()

        response = agent.run_task(task["prompt"])

        # Check expected tools
        tools_used = [tc["name"] for tc in response.tool_calls]
        expected = task.get("expected_tools", [])
        tools_match = set(expected).issubset(set(tools_used)) if expected else True

        # Check expected answer
        expected_answer = task.get("expected_answer_contains")
        answer_match = expected_answer.lower() in response.output.lower() if expected_answer else None

        result = {
            "task_id": task["id"],
            "description": task["description"],
            "prompt": task["prompt"],
            "output": response.output[:500],
            "tools_used": tools_used,
            "expected_tools": expected,
            "tools_match": tools_match,
            "expected_answer_contains": expected_answer,
            "answer_match": answer_match,
            "duration_ms": response.duration_ms,
            "error": response.error,
        }
        results.append(result)

        status = "PASS" if (tools_match and answer_match is not False) else "WARN"
        print(f"  Output: {response.output[:200]}")
        print(f"  Tools: {tools_used} (expected: {expected}) → {'OK' if tools_match else 'MISMATCH'}")
        if expected_answer:
            print(f"  Answer contains '{expected_answer}': {answer_match}")
        print(f"  Duration: {response.duration_ms}ms | Status: {status}")

        logger.info(f"{task['id']}: {status}", extra={"extra_data": result})

    # Write summary
    passed = sum(1 for r in results if r["tools_match"] and r.get("answer_match") is not False)
    summary = {
        "agent": agent_name,
        "seed": seed,
        "total_tasks": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": passed / len(results) if results else 0,
        "results": results,
    }
    output_dir = f"outputs/baselines/{agent_name}_seed{seed}"
    write_summary_json(f"{output_dir}/summary.json", summary)

    print(f"\n{'='*60}")
    print(f"Baseline Results: {passed}/{len(results)} passed ({summary['pass_rate']:.0%})")
    print(f"Summary: {output_dir}/summary.json")


def main():
    parser = argparse.ArgumentParser(description="Run baseline tasks on agent targets")
    parser.add_argument("--agent", default="langchain_react", help="Agent target name")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--task", default=None, help="Run specific task by ID (e.g., BL-001)")
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls")
    parser.add_argument("--config", default="config/base.yaml", help="Config file")
    args = parser.parse_args()

    run_baselines(args.agent, args.seed, args.task, args.dry_run)


if __name__ == "__main__":
    main()
